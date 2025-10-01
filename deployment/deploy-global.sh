#!/bin/bash

# Global Multi-Region Deployment Script for Movie Recap Service
# This script deploys the application across multiple regions for worldwide availability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGIONS=("us-east-1" "eu-west-1" "ap-southeast-1" "us-west-2")
ENVIRONMENTS=("staging" "production")
PROJECT_NAME="movie-recap-service"
DOCKER_REGISTRY="your-registry.com"  # Replace with your registry

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "============================================="
    echo "   Movie Recap Service - Global Deployment"
    echo "============================================="
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --region REGION        Deploy to specific region (us-east-1, eu-west-1, ap-southeast-1, us-west-2)"
    echo "  -e, --env ENVIRONMENT      Environment (staging, production)"
    echo "  -a, --all-regions          Deploy to all regions"
    echo "  -b, --build-only           Only build Docker images"
    echo "  -d, --deploy-only          Only deploy (skip build)"
    echo "  -s, --setup-infra          Setup infrastructure (databases, CDN, etc.)"
    echo "  -m, --migrate-db           Run database migrations"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -r us-east-1 -e production    # Deploy to US East 1 production"
    echo "  $0 -a -e staging                  # Deploy to all regions staging"
    echo "  $0 -s -r eu-west-1                # Setup infrastructure in EU West 1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "aws" "kubectl" "terraform")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

validate_region() {
    local region=$1
    
    for valid_region in "${REGIONS[@]}"; do
        if [[ "$region" == "$valid_region" ]]; then
            return 0
        fi
    done
    
    log_error "Invalid region: $region"
    log_info "Valid regions: ${REGIONS[*]}"
    exit 1
}

validate_environment() {
    local env=$1
    
    for valid_env in "${ENVIRONMENTS[@]}"; do
        if [[ "$env" == "$valid_env" ]]; then
            return 0
        fi
    done
    
    log_error "Invalid environment: $env"
    log_info "Valid environments: ${ENVIRONMENTS[*]}"
    exit 1
}

build_images() {
    local region=$1
    local env=$2
    
    log_info "Building Docker images for $region ($env)..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t $DOCKER_REGISTRY/$PROJECT_NAME-backend:$env-$region ../backend/
    
    # Build frontend image with region-specific configuration
    log_info "Building frontend image..."
    docker build \
        --build-arg VITE_API_BASE_URL=https://api-$region.movierecap.com \
        --build-arg VITE_CDN_URL=https://cdn-$region.movierecap.com \
        --build-arg VITE_REGION=$region \
        -t $DOCKER_REGISTRY/$PROJECT_NAME-frontend:$env-$region \
        ../frontend/
    
    # Build worker image
    log_info "Building worker image..."
    docker build -t $DOCKER_REGISTRY/$PROJECT_NAME-worker:$env-$region ../backend/
    
    log_success "Images built successfully"
}

push_images() {
    local region=$1
    local env=$2
    
    log_info "Pushing images to registry..."
    
    # Login to registry
    aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $DOCKER_REGISTRY
    
    # Push images
    docker push $DOCKER_REGISTRY/$PROJECT_NAME-backend:$env-$region
    docker push $DOCKER_REGISTRY/$PROJECT_NAME-frontend:$env-$region
    docker push $DOCKER_REGISTRY/$PROJECT_NAME-worker:$env-$region
    
    log_success "Images pushed to registry"
}

setup_infrastructure() {
    local region=$1
    local env=$2
    
    log_info "Setting up infrastructure in $region ($env)..."
    
    # Switch to infrastructure directory
    cd ../infrastructure
    
    # Initialize Terraform
    terraform init
    
    # Select workspace
    terraform workspace select $env-$region || terraform workspace new $env-$region
    
    # Plan infrastructure
    terraform plan \
        -var="region=$region" \
        -var="environment=$env" \
        -var="project_name=$PROJECT_NAME" \
        -out=tfplan
    
    # Apply infrastructure
    read -p "Apply infrastructure changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply tfplan
        log_success "Infrastructure setup completed"
    else
        log_warning "Infrastructure setup skipped"
    fi
    
    cd ../deployment
}

run_migrations() {
    local region=$1
    local env=$2
    
    log_info "Running database migrations for $region ($env)..."
    
    # Load environment variables
    source .env.$env.$region
    
    # Run migrations using Docker
    docker run --rm \
        --env-file .env.$env.$region \
        $DOCKER_REGISTRY/$PROJECT_NAME-backend:$env-$region \
        alembic upgrade head
    
    log_success "Database migrations completed"
}

deploy_application() {
    local region=$1
    local env=$2
    
    log_info "Deploying application to $region ($env)..."
    
    # Create environment-specific compose file
    local compose_file="docker-compose.$env.$region.yml"
    
    # Copy base compose file and customize
    cp docker-compose.global.yml $compose_file
    
    # Load environment variables
    export $(cat .env.$env.$region | xargs)
    
    # Deploy using Docker Swarm or Kubernetes
    if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
        log_info "Deploying to Kubernetes..."
        deploy_to_kubernetes $region $env
    else
        log_info "Deploying with Docker Compose..."
        docker-compose -f $compose_file up -d
    fi
    
    log_success "Application deployed successfully"
}

deploy_to_kubernetes() {
    local region=$1
    local env=$2
    
    # Apply Kubernetes manifests
    kubectl apply -f ../k8s/namespace.yml
    kubectl apply -f ../k8s/$env/
    
    # Update image tags
    kubectl set image deployment/backend backend=$DOCKER_REGISTRY/$PROJECT_NAME-backend:$env-$region -n $PROJECT_NAME-$env
    kubectl set image deployment/frontend frontend=$DOCKER_REGISTRY/$PROJECT_NAME-frontend:$env-$region -n $PROJECT_NAME-$env
    kubectl set image deployment/worker worker=$DOCKER_REGISTRY/$PROJECT_NAME-worker:$env-$region -n $PROJECT_NAME-$env
    
    # Wait for rollout
    kubectl rollout status deployment/backend -n $PROJECT_NAME-$env
    kubectl rollout status deployment/frontend -n $PROJECT_NAME-$env
    kubectl rollout status deployment/worker -n $PROJECT_NAME-$env
}

setup_monitoring() {
    local region=$1
    local env=$2
    
    log_info "Setting up monitoring for $region ($env)..."
    
    # Deploy monitoring stack
    kubectl apply -f ../monitoring/prometheus/
    kubectl apply -f ../monitoring/grafana/
    kubectl apply -f ../monitoring/alertmanager/
    
    log_success "Monitoring setup completed"
}

health_check() {
    local region=$1
    local env=$2
    
    log_info "Running health checks for $region ($env)..."
    
    local api_url="https://api-$region.movierecap.com"
    local frontend_url="https://$region.movierecap.com"
    
    # Check API health
    if curl -f -s "$api_url/health" > /dev/null; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        exit 1
    fi
    
    # Check frontend
    if curl -f -s "$frontend_url" > /dev/null; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."
    
    # Remove old images
    docker image prune -f
    docker system prune -f
    
    log_success "Cleanup completed"
}

main() {
    local region=""
    local env=""
    local all_regions=false
    local build_only=false
    local deploy_only=false
    local setup_infra=false
    local migrate_db=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--region)
                region="$2"
                shift 2
                ;;
            -e|--env)
                env="$2"
                shift 2
                ;;
            -a|--all-regions)
                all_regions=true
                shift
                ;;
            -b|--build-only)
                build_only=true
                shift
                ;;
            -d|--deploy-only)
                deploy_only=true
                shift
                ;;
            -s|--setup-infra)
                setup_infra=true
                shift
                ;;
            -m|--migrate-db)
                migrate_db=true
                shift
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Validate inputs
    if [[ -z "$env" ]]; then
        log_error "Environment is required"
        print_usage
        exit 1
    fi
    
    validate_environment "$env"
    
    if [[ "$all_regions" == true ]]; then
        regions_to_deploy=("${REGIONS[@]}")
    elif [[ -n "$region" ]]; then
        validate_region "$region"
        regions_to_deploy=("$region")
    else
        log_error "Either --region or --all-regions is required"
        print_usage
        exit 1
    fi
    
    check_prerequisites
    
    # Execute deployment for each region
    for deploy_region in "${regions_to_deploy[@]}"; do
        log_info "Processing region: $deploy_region"
        
        if [[ "$setup_infra" == true ]]; then
            setup_infrastructure "$deploy_region" "$env"
        fi
        
        if [[ "$build_only" == false && "$deploy_only" == false ]] || [[ "$build_only" == true ]]; then
            build_images "$deploy_region" "$env"
            push_images "$deploy_region" "$env"
        fi
        
        if [[ "$migrate_db" == true ]]; then
            run_migrations "$deploy_region" "$env"
        fi
        
        if [[ "$build_only" == false && "$deploy_only" == false ]] || [[ "$deploy_only" == true ]]; then
            deploy_application "$deploy_region" "$env"
            setup_monitoring "$deploy_region" "$env"
            
            # Wait a bit for services to start
            sleep 30
            
            health_check "$deploy_region" "$env"
        fi
        
        log_success "Region $deploy_region completed successfully"
    done
    
    cleanup_old_images
    
    log_success "Global deployment completed successfully!"
    log_info "Access your application at:"
    for deploy_region in "${regions_to_deploy[@]}"; do
        echo "  - $deploy_region: https://$deploy_region.movierecap.com"
    done
}

# Run main function with all arguments
main "$@"