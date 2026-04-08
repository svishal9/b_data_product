#!/bin/bash
# Quick reference guide for common SCB Ingestion commands
# Source this file or run individual commands

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
YAML_DIR="$BASE_DIR/yaml"
PYTHON_DIR="$BASE_DIR/python"
NAMESPACE="scb-ingestion"

# ============================================================================
# QUICK START COMMANDS
# ============================================================================

# Build Docker image locally
function build_image() {
    echo "Building SCB ingestion image..."
    docker build -t scb-ingestion:latest -f "$BASE_DIR/Dockerfile" "$BASE_DIR"
}

# Deploy to minikube (complete setup)
function deploy_minikube() {
    echo "Deploying to minikube..."
    bash "$SCRIPT_DIR/deploy-minikube.sh"
}

# Deploy to production (complete setup)
function deploy_production() {
    echo "Deploying to production..."
    bash "$SCRIPT_DIR/deploy-production.sh"
}

# ============================================================================
# JOB MANAGEMENT
# ============================================================================

# Submit ingestion job
function submit_job() {
    echo "Submitting ingestion job..."
    kubectl apply -f "$YAML_DIR/k8s-job.yaml"
}

# Get job status
function job_status() {
    kubectl get job -n "$NAMESPACE" scb-ingest-job
}

# Watch job in real-time
function watch_job() {
    kubectl get job -n "$NAMESPACE" -w
}

# Delete job
function delete_job() {
    kubectl delete job scb-ingest-job -n "$NAMESPACE" --ignore-not-found
}

# ============================================================================
# LOGGING & DEBUGGING
# ============================================================================

# View job logs (last 50 lines)
function job_logs() {
    kubectl logs -n "$NAMESPACE" job/scb-ingest-job --tail=50
}

# Stream job logs (follow)
function job_logs_follow() {
    kubectl logs -n "$NAMESPACE" -f job/scb-ingest-job
}

# Get detailed job info
function job_describe() {
    kubectl describe job scb-ingest-job -n "$NAMESPACE"
}

# List all pods in namespace
function list_pods() {
    kubectl get pods -n "$NAMESPACE"
}

# Get pod logs
function pod_logs() {
    local pod_name="${1:-$(kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion -o jsonpath='{.items[0].metadata.name}')}"
    if [[ -n "$pod_name" ]]; then
        kubectl logs -n "$NAMESPACE" "$pod_name"
    fi
}

# Access pod shell
function pod_shell() {
    local pod_name="${1:-$(kubectl get pods -n "$NAMESPACE" -l app=scb-ingestion -o jsonpath='{.items[0].metadata.name}')}"
    if [[ -n "$pod_name" ]]; then
        kubectl exec -it -n "$NAMESPACE" "$pod_name" -- /bin/bash
    fi
}

# ============================================================================
# CONFIGURATION
# ============================================================================

# Show Atlas configuration
function show_atlas_config() {
    kubectl get configmap scb-atlas-config -n "$NAMESPACE" -o jsonpath='{.data}' | jq .
}

# Update Atlas host
function set_atlas_host() {
    local host="$1"
    if [[ -z "$host" ]]; then
        echo "Usage: set_atlas_host <hostname>"
        return 1
    fi
    kubectl patch configmap scb-atlas-config -n "$NAMESPACE" -p "{\"data\":{\"ATLAS_SERVER_HOST\":\"$host\"}}"
}

# Update Atlas port
function set_atlas_port() {
    local port="$1"
    if [[ -z "$port" ]]; then
        echo "Usage: set_atlas_port <port>"
        return 1
    fi
    kubectl patch configmap scb-atlas-config -n "$NAMESPACE" -p "{\"data\":{\"ATLAS_SERVER_PORT\":\"$port\"}}"
}

# ============================================================================
# WORKBOOK MANAGEMENT
# ============================================================================

# Copy workbook to pod
function upload_workbook() {
    local workbook_path="$1"
    if [[ -z "$workbook_path" ]]; then
        echo "Usage: upload_workbook <path-to-workbook.xlsx>"
        return 1
    fi

    bash "$SCRIPT_DIR/upload-workbook-to-pvc.sh" "$workbook_path"
}

# ============================================================================
# CLEANUP & RESET
# ============================================================================

# Delete all ingestion resources
function cleanup() {
    echo "Cleaning up ingestion resources..."
    kubectl delete job -n "$NAMESPACE" --all 2>/dev/null || true
    kubectl delete cronjob -n "$NAMESPACE" --all 2>/dev/null || true
    kubectl delete pvc -n "$NAMESPACE" --all 2>/dev/null || true
    echo "Cleanup complete"
}

# Delete namespace (complete reset)
function reset() {
    read -p "Delete entire namespace? This cannot be undone. (yes/no): " confirm
    if [[ "$confirm" == "yes" ]]; then
        kubectl delete namespace "$NAMESPACE"
        echo "Namespace deleted"
    fi
}

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

# Run deployment tests
function run_tests() {
    cd "$PYTHON_DIR"
    pytest test_deployment.py -v
    pytest test_docker_build.py -v
}

# Validate Kubernetes manifests
function validate_manifests() {
    echo "Validating Kubernetes manifests..."
    kubectl apply -f "$YAML_DIR/k8s-setup.yaml" --dry-run=client
    kubectl apply -f "$YAML_DIR/k8s-job.yaml" --dry-run=client
    echo "✓ Manifests are valid"
}

# Health check
function health_check() {
    echo "=== Health Check ==="

    echo -n "Kubernetes: "
    kubectl cluster-info &>/dev/null && echo "✓" || echo "✗"

    echo -n "Namespace: "
    kubectl get namespace "$NAMESPACE" &>/dev/null && echo "✓" || echo "✗"

    echo -n "Docker: "
    docker version &>/dev/null && echo "✓" || echo "✗"

    echo -n "Image: "
    docker images | grep -q "scb-ingestion" && echo "✓" || echo "✗"

    echo -n "ConfigMap: "
    kubectl get configmap scb-atlas-config -n "$NAMESPACE" &>/dev/null && echo "✓" || echo "✗"

    echo -n "PVC: "
    kubectl get pvc scb-workbooks-pvc -n "$NAMESPACE" &>/dev/null && echo "✓" || echo "✗"
}

# ============================================================================
# INFORMATION & HELP
# ============================================================================

# Show all available functions
function show_functions() {
    echo "Available commands:"
    echo ""
    echo "BUILD:"
    echo "  build_image                 - Build Docker image"
    echo ""
    echo "DEPLOYMENT:"
    echo "  deploy_minikube             - Deploy to minikube"
    echo "  deploy_production           - Deploy to production"
    echo ""
    echo "JOB MANAGEMENT:"
    echo "  submit_job                  - Submit ingestion job"
    echo "  job_status                  - Get job status"
    echo "  watch_job                   - Watch job progress"
    echo "  delete_job                  - Delete job"
    echo ""
    echo "LOGGING:"
    echo "  job_logs                    - View job logs"
    echo "  job_logs_follow             - Follow job logs"
    echo "  job_describe                - Describe job"
    echo "  list_pods                   - List pods"
    echo "  pod_logs [pod-name]         - Get pod logs"
    echo "  pod_shell [pod-name]        - Access pod shell"
    echo ""
    echo "CONFIGURATION:"
    echo "  show_atlas_config           - Show Atlas configuration"
    echo "  set_atlas_host <host>       - Update Atlas host"
    echo "  set_atlas_port <port>       - Update Atlas port"
    echo ""
    echo "WORKBOOKS:"
    echo "  upload_workbook <path>      - Upload workbook to pod"
    echo ""
    echo "CLEANUP:"
    echo "  cleanup                     - Delete all resources"
    echo "  reset                       - Delete namespace"
    echo ""
    echo "TESTING:"
    echo "  run_tests                   - Run test suite"
    echo "  validate_manifests          - Validate YAML files"
    echo "  health_check                - Check system health"
}

# Print usage
if [[ $# -eq 0 ]]; then
    show_functions
fi

