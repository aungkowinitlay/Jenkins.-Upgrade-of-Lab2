pipeline {
    agent none
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DOCKERHUB_CREDENTIALS')
        BACKEND_IMAGE = "aungkowin/flask-backend:${env.BUILD_NUMBER}"
        FRONTEND_IMAGE = "aungkowin/nginx-frontend:${env.BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            agent { label 'VM1' }
            steps {
                git branch: 'main', url: 'https://github.com/aungkowinitlay/Jenkins.-Upgrade-of-Lab2.git'
                stash name: 'workspace', includes: 'docker-compose.yml'
            }
        }
        stage('Test VM2 Connection') {
            agent { label 'VM2' }
            steps {
                sh 'echo "Successfully connected to VM2"'
            }
        }
        stage('Build Images') {
            agent { label 'VM1' }
            parallel {
                stage('Build Backend Image') {
                    steps {
                        sh "docker build -t ${BACKEND_IMAGE} -f backend/Dockerfile ./backend"
                    }
                }
                stage('Build Frontend Image') {
                    steps {
                        sh "docker build -t ${FRONTEND_IMAGE} -f frontend/Dockerfile ./frontend"
                    }
                }
            }
        }
        stage('Test Backend') {
            agent { label 'VM1' }
            steps {
                sh "docker run --rm ${BACKEND_IMAGE} pytest"
            }
        }
        stage('Login to Docker Hub') {
            agent { label 'VM1' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_PSW')]) {
                    sh "echo \$DOCKERHUB_PSW | docker login -u \$DOCKERHUB_USR --password-stdin"
                }
            }
        }
        stage('Push Images') {
            agent { label 'VM1' }
            steps {
                sh """
                    docker push ${BACKEND_IMAGE}
                    docker push ${FRONTEND_IMAGE}
                """
            }
        }
        stage('Deploy Backend') {
            agent { label 'VM3' }
            steps {
                unstash 'workspace'
                sh """
                    if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found"; exit 1; fi
                    docker-compose -f docker-compose.yml down || true
                    docker-compose -f docker-compose.yml up -d flask-backend
                """
            }
        }
        stage('Deploy Frontend') {
            agent { label 'VM2' }
            steps {
                unstash 'workspace'
                sh """
                    if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found"; exit 1; fi
                    docker-compose -f docker-compose.yml down || true
                    docker-compose -f docker-compose.yml up -d nginx-frontend
                """
            }
        }
    }
    post {
        always {
            node('VM1') {
                sh "docker logout"
                sh "docker image prune -f"
            }
        }
        success {
            node('VM1') {
                echo "Pipeline completed successfully!"
            }
        }
        failure {
            node('VM1') {
                echo "Pipeline failed!"
            }
        }
    }
}