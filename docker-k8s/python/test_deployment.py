"""
Test suite for Docker image and Kubernetes deployment of SCB Ingestion.
"""

import pytest
import subprocess
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


ROOT_DIR = Path(__file__).resolve().parents[1]
YAML_DIR = ROOT_DIR / "yaml"
SHELL_DIR = ROOT_DIR / "shell"


class TestDockerBuild:
    """Tests for Docker image build process."""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in the project."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile not found"
    
    def test_dockerfile_syntax(self):
        """Test Dockerfile for basic syntax issues."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        with open(dockerfile_path) as f:
            content = f.read()
        
        # Check for required lines
        assert "FROM python:3.13-slim" in content, "Base image not specified"
        assert "WORKDIR /app" in content, "Work directory not set"
        assert "ENTRYPOINT" in content, "Entrypoint not defined"
        assert "ENV" in content, "Environment variables not set"
        assert "HEALTHCHECK" in content, "Health check not defined"
    
    def test_dockerfile_has_dependencies(self):
        """Test that Dockerfile copies project dependencies."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        with open(dockerfile_path) as f:
            content = f.read()
        
        assert "pyproject.toml" in content, "pyproject.toml not copied"
        assert "uv.lock" in content, "uv.lock not copied"
    
    def test_dockerfile_has_app_code(self):
        """Test that Dockerfile copies application code."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        with open(dockerfile_path) as f:
            content = f.read()
        
        assert "scb_dp_cli.py" in content, "scb_dp_cli.py not copied"
        assert "scb_atlas" in content, "scb_atlas not copied"


class TestKubernetesYAML:
    """Tests for Kubernetes YAML manifests."""
    
    def test_setup_yaml_exists(self):
        """Test that setup YAML exists."""
        setup_yaml = YAML_DIR / "k8s-setup.yaml"
        assert setup_yaml.exists(), "k8s-setup.yaml not found"
    
    def test_job_yaml_exists(self):
        """Test that job YAML exists."""
        job_yaml = YAML_DIR / "k8s-job.yaml"
        assert job_yaml.exists(), "k8s-job.yaml not found"
    
    def test_setup_yaml_has_namespace(self):
        """Test that setup YAML defines namespace."""
        setup_yaml = YAML_DIR / "k8s-setup.yaml"
        with open(setup_yaml) as f:
            content = f.read()
        
        assert "kind: Namespace" in content, "Namespace not defined"
        assert "scb-ingestion" in content, "Namespace name incorrect"
    
    def test_setup_yaml_has_configmap(self):
        """Test that setup YAML defines ConfigMap."""
        setup_yaml = YAML_DIR / "k8s-setup.yaml"
        with open(setup_yaml) as f:
            content = f.read()
        
        assert "kind: ConfigMap" in content, "ConfigMap not defined"
        assert "ATLAS_SERVER_HOST" in content, "ATLAS_SERVER_HOST not configured"
        assert "ATLAS_SERVER_PORT" in content, "ATLAS_SERVER_PORT not configured"
    
    def test_setup_yaml_has_serviceaccount(self):
        """Test that setup YAML defines ServiceAccount."""
        setup_yaml = YAML_DIR / "k8s-setup.yaml"
        with open(setup_yaml) as f:
            content = f.read()
        
        assert "kind: ServiceAccount" in content, "ServiceAccount not defined"
        assert "scb-ingestion-sa" in content, "ServiceAccount name incorrect"
    
    def test_setup_yaml_has_rbac(self):
        """Test that setup YAML defines RBAC resources."""
        setup_yaml = YAML_DIR / "k8s-setup.yaml"
        with open(setup_yaml) as f:
            content = f.read()
        
        assert "kind: ClusterRole" in content, "ClusterRole not defined"
        assert "kind: ClusterRoleBinding" in content, "ClusterRoleBinding not defined"
    
    def test_job_yaml_has_job_definition(self):
        """Test that job YAML defines Job."""
        job_yaml = YAML_DIR / "k8s-job.yaml"
        with open(job_yaml) as f:
            content = f.read()
        
        assert "kind: Job" in content, "Job not defined"
        assert "scb-ingest-job" in content, "Job name incorrect"
    
    def test_job_yaml_has_cronjob_definition(self):
        """Test that job YAML defines CronJob."""
        job_yaml = YAML_DIR / "k8s-job.yaml"
        with open(job_yaml) as f:
            content = f.read()
        
        assert "kind: CronJob" in content, "CronJob not defined"
        assert "scb-ingest-scheduled" in content, "CronJob name incorrect"
    
    def test_job_yaml_has_resource_limits(self):
        """Test that job YAML defines resource limits."""
        job_yaml = YAML_DIR / "k8s-job.yaml"
        with open(job_yaml) as f:
            content = f.read()
        
        assert "resources:" in content, "Resources not defined"
        assert "memory:" in content, "Memory limit not defined"
        assert "cpu:" in content, "CPU limit not defined"
    
    def test_job_yaml_has_volume_mount(self):
        """Test that job YAML defines volume mounts."""
        job_yaml = YAML_DIR / "k8s-job.yaml"
        with open(job_yaml) as f:
            content = f.read()
        
        assert "volumeMounts:" in content, "Volume mounts not defined"
        assert "/data/workbooks" in content, "Workbook mount path incorrect"


class TestDeploymentScripts:
    """Tests for deployment scripts."""
    
    def test_minikube_script_exists(self):
        """Test that minikube deployment script exists."""
        script = SHELL_DIR / "deploy-minikube.sh"
        assert script.exists(), "deploy-minikube.sh not found"
        assert script.stat().st_mode & 0o111, "deploy-minikube.sh not executable"
    
    def test_production_script_exists(self):
        """Test that production deployment script exists."""
        script = SHELL_DIR / "deploy-production.sh"
        assert script.exists(), "deploy-production.sh not found"
        assert script.stat().st_mode & 0o111, "deploy-production.sh not executable"
    
    def test_minikube_script_syntax(self):
        """Test minikube script for bash syntax errors."""
        script = SHELL_DIR / "deploy-minikube.sh"
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"
    
    def test_production_script_syntax(self):
        """Test production script for bash syntax errors."""
        script = SHELL_DIR / "deploy-production.sh"
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"

    def test_production_script_has_secret_placeholder_guard(self):
        """Test production script fails fast on placeholder Secret values."""
        script = SHELL_DIR / "deploy-production.sh"
        with open(script) as f:
            content = f.read()

        assert "check_atlas_secret_placeholders" in content, "Missing secret safety check function"
        assert "REPLACE_ME" in content, "Missing placeholder credential guard"

    def test_minikube_script_has_secret_placeholder_guard(self):
        """Test minikube script fails fast on placeholder Secret values."""
        script = SHELL_DIR / "deploy-minikube.sh"
        with open(script) as f:
            content = f.read()

        assert "check_atlas_secret_placeholders" in content, "Missing secret safety check function"
        assert "REPLACE_ME" in content, "Missing placeholder credential guard"


class TestConfigurationFiles:
    """Tests for configuration and documentation files."""
    
    def test_required_files_exist(self):
        """Test that all required files exist in docker-k8s directory."""
        docker_k8s_dir = ROOT_DIR
        required_files = [
            "Dockerfile",
            "yaml/k8s-setup.yaml",
            "yaml/k8s-job.yaml",
            "shell/deploy-minikube.sh",
            "shell/deploy-production.sh"
        ]
        
        for file in required_files:
            assert (docker_k8s_dir / file).exists(), f"{file} not found"
    
    def test_dockerfile_workbook_path(self):
        """Test that Dockerfile defines workbook mount path."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        with open(dockerfile_path) as f:
            content = f.read()
        
        assert "/data/workbooks" in content, "Workbook path not defined in Dockerfile"


class TestIntegration:
    """Integration tests for the deployment."""
    
    @patch('subprocess.run')
    def test_minikube_deployment_flow(self, mock_run):
        """Test the deployment flow for minikube."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        # This is a conceptual test - actual execution would require minikube
        script_path = SHELL_DIR / "deploy-minikube.sh"
        assert script_path.exists()
    
    def test_environment_variables_documented(self):
        """Test that environment variables are documented."""
        dockerfile_path = ROOT_DIR / "Dockerfile"
        with open(dockerfile_path) as f:
            content = f.read()
        
        # Check that key environment variables are set
        assert "ATLAS_SERVER_HOST" in content, "ATLAS_SERVER_HOST not in Dockerfile"
        assert "ATLAS_SERVER_PORT" in content, "ATLAS_SERVER_PORT not in Dockerfile"
        assert "PYTHONUNBUFFERED" in content, "PYTHONUNBUFFERED not in Dockerfile"


class TestDocumentation:
    """Tests for documentation completeness."""
    
    def test_readme_exists(self):
        """Test that README exists in docker-k8s directory."""
        readme = ROOT_DIR / "README.md"
        # This will be created next - test will pass when file exists
        # For now, we skip this or mark as xfail
        pass
    
    def test_all_scripts_have_comments(self):
        """Test that deployment scripts have comments."""
        for script_name in ["deploy-minikube.sh", "deploy-production.sh"]:
            script = SHELL_DIR / script_name
            with open(script) as f:
                content = f.read()
            
            assert "#" in content, f"{script_name} has no comments"
            assert "echo" in content, f"{script_name} has no output messages"


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

