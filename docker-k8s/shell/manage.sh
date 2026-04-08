#!/bin/bash
# Utility script to manage SCB Ingestion on Kubernetes
# Provides helpful commands for common operations

set -e

NAMESPACE="scb-ingestion"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
YAML_DIR="$BASE_DIR/yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_usage() {
    cat << EOF
${BLUE}SCB Ingestion Management Utility${NC}

Usage: $(basename "$0") <command> [options]

Commands:
  status          Show ingestion job status
  logs            Show ingestion job logs
  deploy          Deploy ingestion job
  delete          Delete all ingestion resources
  describe        Show detailed job description
  watch           Watch job progress in real-time
  shell           Access pod shell for debugging
  restart         Restart the ingestion job
  config          Show current configuration
  health          Check system health
  help            Show this help message

Examples:
  $(basename "$0") status
  $(basename "$0") logs -f
  $(basename "$0") deploy --dry-run
  $(basename "$0") shell
  $(basename "$0") health

Environment Variables:
  NAMESPACE       Kubernetes namespace (default: $NAMESPACE)
  KUBECONFIG      Path to kubeconfig file

EOF
}

# Helper functions
check_namespace() {
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo -e "${RED}✗ Namespace $NAMESPACE not found${NC}"
        return 1
    fi
}

show_status() {
    echo -e "${YELLOW}=== Ingestion Job Status ===${NC}"
    check_namespace || return 1

    kubectl get job -n "$NAMESPACE" scb-ingest-job 2>/dev/null || \
        echo -e "${YELLOW}No job found. Deploy with: $(basename "$0") deploy${NC}"

    echo ""
    echo -e "${YELLOW}=== Pod Status ===${NC}"
    kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion 2>/dev/null || \
        echo -e "${YELLOW}No pods found${NC}"
}

show_logs() {
    echo -e "${YELLOW}=== Job Logs ===${NC}"
    check_namespace || return 1

    # Default to last 50 lines unless -f flag for follow
    if [[ "$*" == *"-f"* ]] || [[ "$*" == *"--follow"* ]]; then
        kubectl logs -n "$NAMESPACE" -f job/scb-ingest-job 2>/dev/null || \
            echo -e "${YELLOW}No logs available. Deploy and run job first.${NC}"
    else
        kubectl logs -n "$NAMESPACE" --tail=50 job/scb-ingest-job 2>/dev/null || \
            echo -e "${YELLOW}No logs available. Deploy and run job first.${NC}"
    fi
}

deploy_job() {
    echo -e "${YELLOW}Deploying ingestion job...${NC}"
    check_namespace || return 1

    if [[ "$*" == *"--dry-run"* ]]; then
        kubectl apply -f "$YAML_DIR/k8s-job.yaml" --dry-run=client
        echo -e "${GREEN}✓ Dry-run complete (no changes made)${NC}"
    else
        kubectl apply -f "$YAML_DIR/k8s-job.yaml"
        echo -e "${GREEN}✓ Job deployed${NC}"
        echo -e "${YELLOW}Monitor with: $(basename "$0") logs -f${NC}"
    fi
}

delete_resources() {
    echo -e "${YELLOW}Deleting ingestion job...${NC}"
    check_namespace || return 1

    read -p "Are you sure? This will delete all ingestion jobs. (yes/no): " confirm
    if [[ "$confirm" == "yes" ]]; then
        kubectl delete job scb-ingest-job -n "$NAMESPACE" 2>/dev/null || true
        kubectl delete cronjob scb-ingest-scheduled -n "$NAMESPACE" 2>/dev/null || true
        echo -e "${GREEN}✓ Resources deleted${NC}"
    else
        echo -e "${YELLOW}Cancelled${NC}"
    fi
}

describe_job() {
    echo -e "${YELLOW}=== Job Description ===${NC}"
    check_namespace || return 1

    kubectl describe job scb-ingest-job -n "$NAMESPACE" 2>/dev/null || \
        echo -e "${RED}Job not found${NC}"

    echo ""
    echo -e "${YELLOW}=== Pod Description ===${NC}"
    pod=$(kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [[ -n "$pod" ]]; then
        kubectl describe pod "$pod" -n "$NAMESPACE"
    else
        echo -e "${YELLOW}No pods found${NC}"
    fi
}

watch_progress() {
    echo -e "${YELLOW}=== Watching Job Progress ===${NC}"
    check_namespace || return 1

    kubectl get job -n "$NAMESPACE" -w 2>/dev/null || \
        echo -e "${YELLOW}No jobs to watch${NC}"
}

access_shell() {
    echo -e "${YELLOW}Accessing pod shell...${NC}"
    check_namespace || return 1

    pod=$(kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [[ -n "$pod" ]]; then
        echo -e "${GREEN}✓ Connecting to pod: $pod${NC}"
        kubectl exec -it "$pod" -n "$NAMESPACE" -- /bin/bash
    else
        echo -e "${RED}✗ No running pods found${NC}"
        return 1
    fi
}

restart_job() {
    echo -e "${YELLOW}Restarting ingestion job...${NC}"
    check_namespace || return 1

    # Delete existing job
    kubectl delete job scb-ingest-job -n "$NAMESPACE" 2>/dev/null || true
    echo -e "${YELLOW}Waiting for pod termination...${NC}"
    sleep 5

    # Redeploy
    kubectl apply -f "$YAML_DIR/k8s-job.yaml"
    echo -e "${GREEN}✓ Job restarted${NC}"
}

show_config() {
    echo -e "${YELLOW}=== Current Configuration ===${NC}"
    check_namespace || return 1

    echo -e "${BLUE}Atlas Configuration:${NC}"
    kubectl get configmap scb-atlas-config -n "$NAMESPACE" -o jsonpath='{.data}' 2>/dev/null | jq . || true

    echo ""
    echo -e "${BLUE}Resource Limits:${NC}"
    kubectl get job scb-ingest-job -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null | jq . || \
        echo -e "${YELLOW}Job not deployed yet${NC}"
}

check_health() {
    echo -e "${YELLOW}=== System Health Check ===${NC}"

    # Check Kubernetes connectivity
    echo -n "Kubernetes API: "
    if kubectl cluster-info &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi

    # Check namespace
    echo -n "Namespace ($NAMESPACE): "
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Check Docker
    echo -n "Docker: "
    if docker --version &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Check image
    echo -n "SCB Ingestion Image: "
    if docker images | grep -q "scb-ingestion"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}! (Not found locally)${NC}"
    fi

    # Check ServiceAccount
    echo -n "ServiceAccount: "
    if kubectl get sa scb-ingestion-sa -n "$NAMESPACE" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Check PVC
    echo -n "Persistent Volume Claim: "
    if kubectl get pvc scb-workbooks-pvc -n "$NAMESPACE" &> /dev/null; then
        pvc_status=$(kubectl get pvc scb-workbooks-pvc -n "$NAMESPACE" -o jsonpath='{.status.phase}')
        if [[ "$pvc_status" == "Bound" ]]; then
            echo -e "${GREEN}✓ (Bound)${NC}"
        else
            echo -e "${YELLOW}! ($pvc_status)${NC}"
        fi
    else
        echo -e "${RED}✗${NC}"
    fi

    echo ""
    echo -e "${YELLOW}=== Recent Events ===${NC}"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -5
}

# Main script logic
if [[ $# -eq 0 ]]; then
    print_usage
    exit 0
fi

case "$1" in
    status)
        show_status
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    deploy)
        shift
        deploy_job "$@"
        ;;
    delete)
        delete_resources
        ;;
    describe)
        describe_job
        ;;
    watch)
        watch_progress
        ;;
    shell)
        access_shell
        ;;
    restart)
        restart_job
        ;;
    config)
        show_config
        ;;
    health)
        check_health
        ;;
    help|-h|--help)
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_usage
        exit 1
        ;;
esac

