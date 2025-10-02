<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'resend' => [
        'key' => env('RESEND_KEY'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    'movie_recap' => [
        'api_url' => env('MOVIE_RECAP_API_URL', 'http://localhost:8000'),
        'api_key' => env('MOVIE_RECAP_API_KEY'),
        'google_drive_credentials_file' => env('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials/google-drive-credentials.json'),
        'google_drive_root_folder' => env('GOOGLE_DRIVE_ROOT_FOLDER', 'movie-recap-pipeline'),
        'colab_webhook_url' => env('COLAB_WEBHOOK_URL', 'https://your-colab-webhook.com/webhook'),
        'colab_webhook_secret' => env('COLAB_WEBHOOK_SECRET', 'colab-webhook-secret'),
        'n8n_webhook_url' => env('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook'),
        'n8n_api_url' => env('N8N_API_URL', 'http://localhost:5678/api/v1'),
        'n8n_api_key' => env('N8N_API_KEY'),
    ],

];
