#!/bin/bash
# Advanced setup script for production-grade SCB Ingestion deployment
# Includes security hardening, monitoring, and best practices

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
NAMESPACE="scb-ingestion"
CONFIG_FILE="${CONFIG_FILE:-$BASE_DIR/yaml/config-template.yaml}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*"
}

print_banner() {
    cat << EOF
${BLUE}
╔═══════════════════════════════════════════════════════════════╗
║   SCB Ingestion - Advanced Production Setup                  ║
║   Kubernetes Deployment with Security & Monitoring           ║
╚═══════════════════════════════════════════════════════════════╝
${NC}
EOF
}

setup_secrets() {
    log_info "Setting up Kubernetes Secrets for credentials..."

    read -s -p "Enter Atlas username: " ATLAS_USER
    echo
    read -s -p "Enter Atlas password: " ATLAS_PASS
    echo

    # Create secret
    kubectl create secret generic scb-atlas-credentials \
        --from-literal=ATLAS_USERNAME="$ATLAS_USER" \
        --from-literal=ATLAS_PASSWORD="$ATLAS_PASS" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    log_success "Secrets created"
}

setup_network_policy() {
    log_info "Setting up Network Policies..."

    cat << 'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scb-ingestion-policy
  namespace: scb-ingestion
spec:
  podSelector:
    matchLabels:
      app: scb-ingestion
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: scb-ingestion
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
  - to:
    - namespaceSelector:
        matchLabels:
          name: atlas-system
    ports:
    - protocol: TCP
      port: 21000
EOF

    log_success "Network policies applied"
}

setup_monitoring() {
    log_info "Setting up Prometheus ServiceMonitor..."

    # Check if Prometheus operator is installed
    if kubectl api-resources | grep -q "servicemonitor"; then
        cat << 'EOF' | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: scb-ingestion
  namespace: scb-ingestion
  labels:
    app: scb-ingestion
spec:
  selector:
    matchLabels:
      app: scb-ingestion
  endpoints:
  - port: metrics
    interval: 30s
EOF
        log_success "ServiceMonitor created"
    else
        log_warning "Prometheus operator not found, skipping ServiceMonitor"
    fi
}

setup_ingress() {
    log_info "Setting up Ingress for monitoring..."

    read -p "Enter domain for Ingress (e.g., ingestion.example.com): " DOMAIN

    if [[ -z "$DOMAIN" ]]; then
        log_warning "Skipping Ingress setup"
        return
    fi

    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scb-ingestion-ingress
  namespace: $NAMESPACE
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - $DOMAIN
    secretName: scb-ingestion-tls
  rules:
  - host: $DOMAIN
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: scb-ingestion-service
            port:
              number: 8080
EOF

    log_success "Ingress created for $DOMAIN"
}

setup_pod_security_policy() {
    log_info "Setting up Pod Security Policy..."

    cat << 'EOF' | kubectl apply -f -
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: scb-ingestion-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: false
EOF

    log_success "Pod Security Policy created"
}

setup_rbac_advanced() {
    log_info "Setting up advanced RBAC..."

    cat << 'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: scb-ingestion-role
  namespace: scb-ingestion
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: scb-ingestion-rolebinding
  namespace: scb-ingestion
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: scb-ingestion-role
subjects:
- kind: ServiceAccount
  name: scb-ingestion-sa
  namespace: scb-ingestion
EOF

    log_success "Advanced RBAC configured"
}

setup_logging() {
    log_info "Setting up centralized logging..."

    # Check if ELK stack is available
    if kubectl api-resources | grep -q "logstash"; then
        log_info "ELK stack detected, configuring..."
        cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: scb-ingestion-logging
  namespace: scb-ingestion
data:
  logstash.conf: |
    input {
      kubernetes {
        namespace => "scb-ingestion"
        app => "scb-ingestion"
      }
    }
    filter {
      json {
        source => "message"
      }
    }
    output {
      elasticsearch {
        hosts => ["elasticsearch:9200"]
        index => "scb-ingestion-%{+YYYY.MM.dd}"
      }
    }
EOF
        log_success "Logging configured"
    else
        log_warning "ELK stack not found, skipping logging setup"
    fi
}

setup_backup_restore() {
    log_info "Setting up backup strategy..."

    cat << 'EOF' > "$SCRIPT_DIR/backup-workbooks.sh"
#!/bin/bash
# Backup script for workbook PVC

NAMESPACE="scb-ingestion"
PVC_NAME="scb-workbooks-pvc"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Create backup
kubectl exec -n "$NAMESPACE" -it \
  $(kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion -o jsonpath='{.items[0].metadata.name}') \
  -- tar czf - /data/workbooks > "$BACKUP_DIR/workbooks_$TIMESTAMP.tar.gz"

echo "Backup created: $BACKUP_DIR/workbooks_$TIMESTAMP.tar.gz"
EOF

    chmod +x "$SCRIPT_DIR/backup-workbooks.sh"
    log_success "Backup script created"
}

setup_audit_logging() {
    log_info "Setting up audit logging..."

    cat << 'EOF' | kubectl apply -f -
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  omitStages:
  - RequestReceived
  resources:
  - group: ""
    resources: ["pods"]
  namespaces: ["scb-ingestion"]
- level: Metadata
  omitStages:
  - RequestReceived
  resources:
  - group: "batch"
    resources: ["jobs"]
  namespaces: ["scb-ingestion"]
EOF

    log_success "Audit logging configured"
}

verify_setup() {
    log_info "Verifying setup..."

    echo ""
    echo -e "${BLUE}=== Resource Status ===${NC}"

    echo -n "Namespace: "
    kubectl get namespace "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

    echo -n "ServiceAccount: "
    kubectl get sa scb-ingestion-sa -n "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

    echo -n "ConfigMap: "
    kubectl get configmap scb-atlas-config -n "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

    echo -n "Secret: "
    kubectl get secret scb-atlas-credentials -n "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}✗${NC}"

    echo -n "PVC: "
    kubectl get pvc scb-workbooks-pvc -n "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

    echo -n "RBAC: "
    kubectl get role scb-ingestion-role -n "$NAMESPACE" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

    echo ""
}

main() {
    print_banner

    # Check prerequisites
    log_info "Checking prerequisites..."

    for cmd in kubectl docker; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd not found"
            exit 1
        fi
    done

    log_success "Prerequisites met"

    # Get confirmation
    echo ""
    log_info "This script will set up:"
    echo "  1. Kubernetes Secrets for credentials"
    echo "  2. Network Policies"
    echo "  3. Monitoring (if Prometheus available)"
    echo "  4. Pod Security Policies"
    echo "  5. Advanced RBAC"
    echo "  6. Logging configuration"
    echo "  7. Backup strategies"
    echo ""

    read -p "Continue with advanced setup? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        log_warning "Setup cancelled"
        exit 0
    fi

    # Run setup steps
    setup_secrets
    setup_network_policy
    setup_pod_security_policy
    setup_rbac_advanced
    setup_logging
    setup_backup_restore
    setup_audit_logging

    # Optional: Setup monitoring
    read -p "Set up monitoring? (yes/no): " monitor
    if [[ "$monitor" == "yes" ]]; then
        setup_monitoring
    fi

    # Optional: Setup ingress
    read -p "Set up Ingress? (yes/no): " ingress
    if [[ "$ingress" == "yes" ]]; then
        setup_ingress
    fi

    # Verify
    verify_setup

    echo ""
    log_success "Advanced setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy the ingestion job:"
    echo "     kubectl apply -f k8s-job.yaml"
    echo ""
    echo "  2. Monitor deployment:"
    echo "     kubectl get job -n $NAMESPACE -w"
    echo ""
    echo "  3. View logs:"
    echo "     kubectl logs -n $NAMESPACE -f job/scb-ingest-job"
}

main "$@"

