# BTP Engine HTTP Service Deployment

## Prerequisites

- Docker installed locally (for building)
- Cloud provider account (Render, Fly.io, or Google Cloud Run)
- GitHub repository access

## Deployment Options

### Option 1: Render

1. **Create Render account** at https://render.com

2. **Create New Web Service**
   - Connect your GitHub repository: `phippsou-dev/btp-engine-core`
   - Branch: `feature/http-service-lovable-contract`
   - Runtime: Docker
   - Region: Choose closest to your users
   - Instance Type: Free or Starter

3. **Environment Variables**
   ```
   BTP_ENGINE_TOKEN=<generate-random-token>
   ```

4. **Deploy Settings**
   - Docker Command: `uvicorn service.app:app --host 0.0.0.0 --port 8080`
   - Port: 8080

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note the public URL (e.g., `https://btp-engine-core.onrender.com`)

6. **Verify**
   ```bash
   curl https://btp-engine-core.onrender.com/health
   ```

### Option 2: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Initialize app**
   ```bash
   cd /path/to/btp-engine-core
   fly launch --no-deploy
   ```

4. **Configure fly.toml**
   ```toml
   app = "btp-engine-core"
   
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     PORT = "8080"
   
   [[services]]
     internal_port = 8080
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

5. **Set secrets**
   ```bash
   fly secrets set BTP_ENGINE_TOKEN=$(openssl rand -hex 32)
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

7. **Get URL**
   ```bash
   fly info
   ```

### Option 3: Google Cloud Run

1. **Install gcloud CLI**
   ```bash
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Initialize**
   ```bash
   gcloud init
   gcloud auth configure-docker
   ```

3. **Build and push image**
   ```bash
   cd /path/to/btp-engine-core
   
   PROJECT_ID=$(gcloud config get-value project)
   IMAGE_NAME="gcr.io/${PROJECT_ID}/btp-engine-core"
   
   docker build -t $IMAGE_NAME .
   docker push $IMAGE_NAME
   ```

4. **Deploy to Cloud Run**
   ```bash
   BTP_TOKEN=$(openssl rand -hex 32)
   
   gcloud run deploy btp-engine-core \
     --image $IMAGE_NAME \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars BTP_ENGINE_TOKEN=$BTP_TOKEN \
     --port 8080
   ```

5. **Get URL**
   ```bash
   gcloud run services describe btp-engine-core \
     --platform managed \
     --region us-central1 \
     --format 'value(status.url)'
   ```

## Generate Secure Token

Generate a random token for `BTP_ENGINE_TOKEN`:

```bash
# Linux/Mac
openssl rand -hex 32

# Or using Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Verify Deployment

1. **Health check**
   ```bash
   curl https://your-service-url/health
   ```

   Expected response:
   ```json
   {
     "ok": true,
     "service": "btp-engine-core",
     "mode": "deterministic",
     "guardrails_ok": true
   }
   ```

2. **Test with file** (requires PDF file)
   ```bash
   curl -X POST https://your-service-url/run \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test.pdf" \
     -F "mode=dry_run"
   ```

## Configuration for MyHome/Lovable

Once deployed, configure in Lovable:

1. **Environment Variables**
   ```
   BTP_ENGINE_URL=https://your-service-url
   BTP_ENGINE_TOKEN=your-generated-token
   ```

2. **Edge Function** should call:
   ```typescript
   const response = await fetch(`${BTP_ENGINE_URL}/run`, {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${BTP_ENGINE_TOKEN}`
     },
     body: formData
   });
   ```

## Monitoring

- **Render**: Check logs in Render dashboard
- **Fly.io**: `fly logs`
- **Cloud Run**: Check Cloud Console logs

## Troubleshooting

### Service not responding
- Check logs for errors
- Verify environment variables are set
- Check memory/CPU limits

### Authentication errors
- Verify `BTP_ENGINE_TOKEN` matches in service and client
- Check Authorization header format: `Bearer <token>`

### File upload errors
- Verify Content-Type is `multipart/form-data`
- Check file size limits (adjust in cloud provider settings)
- Ensure file field name is exactly `file`

### Engine errors
- Check that all system dependencies are installed (tesseract, poppler)
- Verify input files are valid PDFs
- Check temp directory permissions
