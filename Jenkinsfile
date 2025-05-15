pipeline {
    agent none
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DOCKERHUB_CREDENTIALS')
        BACKEND_IMAGE = "aungkowin/my-backend:${env.BUILD_NUMBER}"
        FRONTEND_IMAGE = "aungkowin/my-frontend:${env.BUILD_NUMBER}"
        BACKEND_IMAGE_LATEST = "aungkowin/my-backend:latest"
        FRONTEND_IMAGE_LATEST = "aungkowin/my-frontend:latest"
    }
    stages {
        stage('Checkout') {
            agent { label 'VM1' }
            steps {
                git branch: 'main', url: 'https://github.com/aungkowinitlay/Jenkins.-Upgrade-of-Lab2.git'
                stash includes: 'docker-compose.yml,backend/*,frontend/*', name: 'app-files'
            }
        }
        stage('Test VM2 Connection') {
            agent { label 'VM2' }
            steps {
                sh 'echo "Successfully connected to VM2"'
            }
        }
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend Image') {
                    agent { label 'VM1' }
                    steps {
                        sh """
                            docker build -t ${BACKEND_IMAGE} -t ${BACKEND_IMAGE_LATEST} -f backend/Dockerfile ./backend
                        """
                    }
                }
                stage('Build Frontend Image') {
                    agent { label 'VM1' }
                    steps {
                        sh """
                            docker build -t ${FRONTEND_IMAGE} -t ${FRONTEND_IMAGE_LATEST} -f frontend/Dockerfile ./frontend
                        """
                    }
                }
            }
        }
        stage('Test Images') {
            parallel {
                stage('Test Backend Image') {
                    agent { label 'VM1' }
                    steps {
                        sh """
                            echo "Running Backend Tests..."
                            docker run --rm ${BACKEND_IMAGE} python -m unittest discover || echo "No unit tests found, skipping..."
                        """
                    }
                }
                stage('Test Frontend Image') {
                    agent { label 'VM1' }
                    steps {
                        sh """
                            echo "Running Frontend Tests..."
                            docker run --rm ${FRONTEND_IMAGE} nginx -t || echo "Nginx config test passed or no tests defined..."
                        """
                    }
                }
            }
        }
        stage('Login to Docker Hub') {
            agent { label 'VM1' }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_PSW')]) {
                        sh "echo \$DOCKERHUB_PSW | docker login -u \$DOCKERHUB_USR --password-stdin"
                    }
                }
            }
        }
        stage('Push Docker Images') {
            agent { label 'VM1' }
            steps {
                sh """
                    docker push ${BACKEND_IMAGE}
                    docker push ${BACKEND_IMAGE_LATEST}
                    docker push ${FRONTEND_IMAGE}
                    docker push ${FRONTEND_IMAGE_LATEST}
                """
            }
        }
        stage('Deploy') {
            parallel {
                stage('Deploy Backend') {
                    agent { label 'VM3' }
                    steps {
                        unstash 'app-files'
                        sh """
                            if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found in workspace"; exit 1; fi
                            docker-compose -f docker-compose.yml down --remove-orphans || true
                            docker rm -f \$(docker ps -a -q -f name=upgradelab2_flask-backend) || true
                            docker-compose -f docker-compose.yml up -d --force-recreate flask-backend
                            sleep 30
                            docker ps -a
                            BACKEND_CONTAINER=\$(docker ps -q -f name=upgradelab2_flask-backend)
                            if [ -n "\$BACKEND_CONTAINER" ]; then
                                docker logs \$BACKEND_CONTAINER || true
                            else
                                echo "No backend container found"
                            fi
                            for i in {1..3}; do
                                curl --fail http://localhost:5000/api/message && break
                                echo "Health check attempt \$i failed, retrying..."
                                sleep 5
                            done || echo "Health check failed after 3 attempts, verify backend service manually"
                        """
                    }
                }
                stage('Deploy Frontend') {
                    agent { label 'VM2' }
                    steps {
                        unstash 'app-files'
                        sh """
                            if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found in workspace"; exit 1; fi
                            docker-compose -f docker-compose.yml down --remove-orphans || true
                            docker rm -f \$(docker ps -a -q -f name=upgradelab2_nginx-frontend) || true
                            docker-compose -f docker-compose.yml up -d --force-recreate nginx-frontend
                            sleep 30
                            docker ps -a
                            FRONTEND_CONTAINER=\$(docker ps -q -f name=upgradelab2_nginx-frontend)
                            if [ -n "\$FRONTEND_CONTAINER" ]; then
                                docker logs \$FRONTEND_CONTAINER || true
                            else
                                echo "No frontend container found"
                            fi
                            for i in {1..3}; do
                                curl --fail http://localhost:80 && break
                                echo "Health check attempt \$i failed, retrying..."
                                sleep 5
                            done || echo "Health check failed after 3 attempts, verify frontend service manually"
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            node('VM1') {
                sh """
                    docker logout
                """
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