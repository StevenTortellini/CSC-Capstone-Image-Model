# Food-101 Classifier API (Hugging Face + FastAPI)

This is a minimal FastAPI service that uses a pretrained **Food-101** model from Hugging Face (`nateraw/food`) to classify meal photos. It returns the top-K predictions with confidences and is ready to be called from a web or mobile app.

## 1) Setup (Local, macOS M-series supported)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> On Apple Silicon (M1–M4), PyTorch will automatically use **Metal (MPS)** if available.

## 2) Run the API
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Open interactive docs: `http://127.0.0.1:8000/docs`

Test with curl:
```bash
curl -X POST "http://127.0.0.1:8000/predict_food" \
  -H "accept: application/json" -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/meal.jpg"
```

## 3) Simple Browser Client
Open `client.html` in your browser while the API is running. It will POST the selected image to `/predict_food` and show JSON results.

## 4) Docker (optional)
```bash
docker build -t food101-api .
docker run -p 8000:8000 food101-api
```
Then visit `http://127.0.0.1:8000/docs`

## 5) Deploying (Render/Railway/Heroku)
- Use this repo as your project.
- **Start command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- On first run, the model will download automatically (cached thereafter).
- For Docker-based deploys, use the provided `Dockerfile` (it pre-caches the model at build time).

## 6) Calling from Laravel (example)
```php
$client = new \GuzzleHttp\Client();
$response = $client->post('http://YOUR_API_HOST/predict_food', [
    'multipart' => [[
        'name'     => 'file',
        'contents' => fopen($request->file('image')->getRealPath(), 'r'),
        'filename' => $request->file('image')->getClientOriginalName(),
    ]]
]);
return response()->json(json_decode($response->getBody(), true));
```

## Notes
- Model: [`nateraw/food`](https://huggingface.co/nateraw/food) (EfficientNet fine-tuned on Food-101).
- Endpoint: `POST /predict_food` (multipart/form-data with `file`).
- For production, restrict CORS in `app.py` to your domains.
# redeploy
