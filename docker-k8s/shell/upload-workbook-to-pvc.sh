#!/bin/bash
# Upload a local workbook file into the ingestion PVC at /data/workbooks.

set -euo pipefail

NAMESPACE="scb-ingestion"
PVC_NAME="scb-workbooks-pvc"
TARGET_NAME="metadata.xlsx"
KEEP_HELPER_POD=false
LOCAL_FILE=""
HELPER_POD_NAME="pvc-uploader"

usage() {
  cat <<EOF
Usage: $(basename "$0") <local-workbook-path> [options]

Options:
  --namespace <name>      Kubernetes namespace (default: scb-ingestion)
  --pvc <name>            PVC name (default: scb-workbooks-pvc)
  --target-name <name>    Target filename in /data/workbooks (default: metadata.xlsx)
  --keep-helper-pod       Do not delete helper pod after upload
  -h, --help              Show help

Example:
  $(basename "$0") /path/to/metadata_example.xlsx
  $(basename "$0") /path/to/custom.xlsx --target-name custom.xlsx
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --pvc)
      PVC_NAME="$2"
      shift 2
      ;;
    --target-name)
      TARGET_NAME="$2"
      shift 2
      ;;
    --keep-helper-pod)
      KEEP_HELPER_POD=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
    *)
      if [[ -z "$LOCAL_FILE" ]]; then
        LOCAL_FILE="$1"
      else
        echo "Unexpected argument: $1"
        usage
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$LOCAL_FILE" ]]; then
  echo "Missing required local workbook path."
  usage
  exit 1
fi

if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "Local file not found: $LOCAL_FILE"
  exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed or not in PATH."
  exit 1
fi

if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
  echo "Namespace not found: $NAMESPACE"
  exit 1
fi

if ! kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
  echo "PVC not found: $PVC_NAME (namespace: $NAMESPACE)"
  exit 1
fi

PVC_PHASE=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [[ "$PVC_PHASE" != "Bound" ]]; then
  echo "PVC $PVC_NAME is not Bound (current phase: $PVC_PHASE)."
  exit 1
fi

cleanup() {
  if [[ "$KEEP_HELPER_POD" = false ]]; then
    kubectl delete pod "$HELPER_POD_NAME" -n "$NAMESPACE" --ignore-not-found >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

kubectl delete pod "$HELPER_POD_NAME" -n "$NAMESPACE" --ignore-not-found >/dev/null 2>&1 || true

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $HELPER_POD_NAME
  namespace: $NAMESPACE
spec:
  restartPolicy: Never
  containers:
    - name: uploader
      image: alpine:3.20
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts:
        - name: workbooks
          mountPath: /data/workbooks
  volumes:
    - name: workbooks
      persistentVolumeClaim:
        claimName: $PVC_NAME
EOF

kubectl wait -n "$NAMESPACE" --for=condition=Ready "pod/$HELPER_POD_NAME" --timeout=90s >/dev/null

kubectl cp "$LOCAL_FILE" "$NAMESPACE/$HELPER_POD_NAME:/data/workbooks/$TARGET_NAME"

kubectl exec -n "$NAMESPACE" "$HELPER_POD_NAME" -- ls -l "/data/workbooks/$TARGET_NAME"

echo "Workbook uploaded successfully: /data/workbooks/$TARGET_NAME"
if [[ "$KEEP_HELPER_POD" = true ]]; then
  echo "Helper pod kept: $HELPER_POD_NAME"
fi

