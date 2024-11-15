pipeline {
    agent any
    tools {
        maven 'Maven'
    }

    stages {
        stage('Git Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/shandrii/distributed-systems-design']])
                echo 'Git Checkout Completed'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sq1') {
                    sh '''mvn clean verify sonar:sonar -Dsonar.projectKey=jenkins-sonar-project -Dsonar.projectName='jenkins-sonar-project' -Dsonar.host.url=http://localhost:9000'''
                    echo 'SonarQube Analysis Completed'
                }
            }
        }
    }
}
