# Best Practices and Security Checklists

## Security Hardening Checklist

**Pod Security:**
- [ ] Enable Pod Security Admission (restricted policy)
- [ ] Run as non-root user (runAsNonRoot: true)
- [ ] Read-only root filesystem (readOnlyRootFilesystem: true)
- [ ] Drop all capabilities, add only required
- [ ] Enable seccomp RuntimeDefault profile
- [ ] Disable privilege escalation (allowPrivilegeEscalation: false)
- [ ] Set resource requests and limits

**Network Security:**
- [ ] Implement default-deny network policies
- [ ] Create explicit allow rules for required traffic
- [ ] Isolate namespaces with network segmentation
- [ ] Use service mesh for mTLS between services
- [ ] Restrict egress to known external endpoints

**Access Control:**
- [ ] Implement RBAC with least privilege
- [ ] Use dedicated service accounts per application
- [ ] Disable automountServiceAccountToken by default
- [ ] Audit and minimize ClusterRole/ClusterRoleBinding usage
- [ ] Rotate service account tokens regularly

**Secrets Management:**
- [ ] Never commit secrets to Git
- [ ] Use external secret management (Vault, ESO)
- [ ] Encrypt secrets at rest in etcd
- [ ] Mount secrets as files, not environment variables
- [ ] Rotate secrets regularly
- [ ] Implement secret access auditing

**Admission Control:**
- [ ] Deploy policy engine (OPA Gatekeeper or Kyverno)
- [ ] Enforce image signature verification
- [ ] Require resource limits on all pods
- [ ] Disallow privileged containers
- [ ] Require security contexts
- [ ] Block deprecated API versions

**Image Security:**
- [ ] Scan images for vulnerabilities (Trivy, Snyk, Clair)
- [ ] Use minimal base images (distroless, Alpine)
- [ ] Sign images with Sigstore/Cosign
- [ ] Use immutable image digests
- [ ] Implement image promotion pipeline
- [ ] Regularly update base images

**Runtime Security:**
- [ ] Deploy runtime security tool (Falco, Sysdig)
- [ ] Monitor for anomalous behavior
- [ ] Enable audit logging
- [ ] Implement intrusion detection
- [ ] Configure alerts for security events

## Common Security Anti-Patterns

1. **Running as root:** Always set runAsNonRoot: true
2. **Privileged containers:** Avoid unless absolutely necessary
3. **Host network/IPC/PID:** Creates shared fate with host
4. **HostPath volumes:** Security risk, avoid in production
5. **Latest image tag:** Not immutable, breaks reproducibility
6. **Secrets in env vars:** Visible in process listings
7. **No network policies:** Unrestricted pod-to-pod traffic
8. **Overly permissive RBAC:** Violates least privilege
9. **No admission control:** Can't enforce policies
10. **Disabled Pod Security:** Allows insecure pod specs

## Compliance Frameworks

**CIS Kubernetes Benchmark:**
- Automated with tools like kube-bench
- Covers control plane, etcd, kubelet, policies
- Regular assessments recommended

**NIST SP 800-190:**
- Container security guidance
- Image, runtime, orchestration controls
- Supply chain security

**PCI-DSS for Kubernetes:**
- Network segmentation requirements
- Access control standards
- Audit logging mandates
- Encryption requirements

## Security Audit Tools

**kube-bench:**
```bash
# Run CIS Kubernetes Benchmark
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

# View results
kubectl logs -f job/kube-bench
```

**kubescape:**
```bash
# Scan cluster for security issues
kubescape scan framework nsa

# Scan specific manifests
kubescape scan deployment.yaml
```

**Falco runtime security:**
```bash
# Install Falco
helm install falco falcosecurity/falco

# Monitor runtime events
kubectl logs -n falco -l app=falco
```
