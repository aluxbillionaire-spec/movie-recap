<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Exception;

class MovieRecapService
{
    protected string $apiUrl;
    protected string $apiKey;
    protected string $googleDriveCredentialsFile;
    protected string $googleDriveRootFolder;
    protected string $colabWebhookUrl;
    protected string $colabWebhookSecret;
    protected string $n8nWebhookUrl;
    protected string $n8nApiUrl;
    protected string $n8nApiKey;

    public function __construct()
    {
        $this->apiUrl = config('services.movie_recap.api_url', 'http://localhost:8000');
        $this->apiKey = config('services.movie_recap.api_key', '');
        $this->googleDriveCredentialsFile = config('services.movie_recap.google_drive_credentials_file', 'credentials/google-drive-credentials.json');
        $this->googleDriveRootFolder = config('services.movie_recap.google_drive_root_folder', 'movie-recap-pipeline');
        $this->colabWebhookUrl = config('services.movie_recap.colab_webhook_url', 'https://your-colab-webhook.com/webhook');
        $this->colabWebhookSecret = config('services.movie_recap.colab_webhook_secret', 'colab-webhook-secret');
        $this->n8nWebhookUrl = config('services.movie_recap.n8n_webhook_url', 'http://localhost:5678/webhook');
        $this->n8nApiUrl = config('services.movie_recap.n8n_api_url', 'http://localhost:5678/api/v1');
        $this->n8nApiKey = config('services.movie_recap.n8n_api_key', '');
    }

    /**
     * Initialize a resumable upload session with the movie-recap backend
     */
    public function initializeUpload(array $uploadData)
    {
        try {
            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json',
            ])->post($this->apiUrl . '/api/v1/uploads/init', $uploadData);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to initialize upload', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during upload initialization', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }

    /**
     * Complete an upload session with the movie-recap backend
     */
    public function completeUpload(string $uploadId, array $completionData = [])
    {
        try {
            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json',
            ])->post($this->apiUrl . '/api/v1/uploads/' . $uploadId . '/complete', $completionData);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to complete upload', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during upload completion', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }

    /**
     * Get upload session status from the movie-recap backend
     */
    public function getUploadStatus(string $uploadId)
    {
        try {
            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $this->apiKey,
            ])->get($this->apiUrl . '/api/v1/uploads/' . $uploadId . '/status');

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to get upload status', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during upload status check', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }

    /**
     * Trigger direct upload to the movie-recap backend
     */
    public function directUpload(array $uploadData, $file)
    {
        try {
            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $this->apiKey,
            ])->attach(
                'file', file_get_contents($file->getRealPath()), $file->getClientOriginalName()
            )->post($this->apiUrl . '/api/v1/uploads/direct', $uploadData);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to perform direct upload', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during direct upload', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }

    /**
     * Trigger processing pipeline via n8n webhook
     */
    public function triggerProcessingPipeline(array $data)
    {
        try {
            $response = Http::withHeaders([
                'Content-Type' => 'application/json',
                'X-Api-Key' => $this->n8nApiKey,
            ])->post($this->n8nWebhookUrl, $data);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to trigger processing pipeline', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during pipeline trigger', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }

    /**
     * Trigger Colab processing via webhook
     */
    public function triggerColabProcessing(array $data)
    {
        try {
            $response = Http::withHeaders([
                'Content-Type' => 'application/json',
                'X-Webhook-Secret' => $this->colabWebhookSecret,
            ])->post($this->colabWebhookUrl, $data);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to trigger Colab processing', [
                'status' => $response->status(),
                'response' => $response->body()
            ]);

            return null;
        } catch (Exception $e) {
            Log::error('Exception during Colab trigger', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }
}
