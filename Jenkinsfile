pipeline {
    agent none

    environment {
        DOCKERHUB_CREDENTIALS = credentials('DOCKERHUB_CREDENTIALS')
        BACKEND_IMAGE = aungkowin/my-backend:latest
        FRONTEND_IMAGE = aungkowin/my-frontend:latest
    }
    stages{
        stage('Checkout'){
            agent {label 'VM1'}
            steps {
                sh """
                git branch: 'main', url: 'https://github.com/aungkowinitlay/Jenkins.-Upgrade-of-Lab2.git'
                """
            }
        }
        stage('Test VM2 connection'){
            agent {label 'VM2'}
            steps {
                sh 'echo"Successfully connected to VM2"'
            }
        }
        stage('Build Docker images') {
            agent {label 'VM1'}
            parallel {
                stage('Build Backend Image'){
                    stpes{
                        sh """
                        docker  build -t ${BACKEND_IMAGE} -f backend/Dockerfile ./backend
                        """
                    }
                }
                stage('Build Frontend Image'){
                    steps {
                        sh """
                        docker build -t ${FRONTEND_IMAGE} -f frontend/Dockerfile ./frontend
                        """
                    }
                }
            }
        }
        stage('Test image'){
            agent {label 'VM1'}
            parallel{
                stage('Test Backend image'){
                    steps{
                        sh """
                        echo "Running Backend Test..."
                        docker rm ${BACKEND_IMAGE}
                        """
                    }
                }
                stage('Test Frontend image'){
                    steps{
                        sh """
                        echo "Running Frontend Test..."
                        docker rm ${FRONTEND_IMAGE}
                        """
                    }
                }
            }
        }
        stage('Login Docker Hub'){
            agent {label 'VM1'}
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_PSW')]) {
                        sh "echo \$DOCKERHUB_PSW | docker login -u \$DOCKERHUB_USR --password-stdin"
                    }
                }
            }
        }
        stage('Push Docker Image'){
            agent {label 'VM1'}
            steps{
                sh """
                docker push ${BACKEND_IMAGE}
                docker push ${FRONTEND_IMAGE}
                """
            }
            
        }
        stage('Deploy') {
            parallel {
                stage('Deploy Backend') {
                    agent { label 'VM3' }
                    steps {
                        git branch: 'main', url: 'https://github.com/aungkowinitlay/Lab2.Jenkins.git'
                        sh """
                            if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found in workspace"; exit 1; fi
                            docker-compose -f docker-compose.yml down || true
                            docker-compose -f docker-compose.yml up -d flask-backend
                        """
                    }
                }
                stage('Deploy Frontend') {
                    agent { label 'VM2' }
                    steps {
                        git branch: 'main', url: 'https://github.com/aungkowinitlay/Lab2.Jenkins.git'
                        sh """
                            if [ ! -f docker-compose.yml ]; then echo "Error: docker-compose.yml not found in workspace"; exit 1; fi
                            docker-compose -f docker-compose.yml down || true
                            docker-compose -f docker-compose.yml up -d nginx-frontend
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