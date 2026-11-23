pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m pip install --user -r requirements.txt'
            }
        }

        stage('Run Pytest') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'SonarQube analysis will be configured after server setup.'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aceest-fitness-gym:latest .'
            }
        }
    }

    post {
        success {
            echo 'ACEest Fitness & Gym CI pipeline completed successfully!'
        }
        failure {
            echo 'CI pipeline failed. Please check the logs.'
        }
    }
}
