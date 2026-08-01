pipeline {
    agent { label 'name1' }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/sadroalin06/dijitalbelge_dokuman.git',
                    credentialsId: 'github-token'
            }
        }

        stage('Sync to target') {
            steps {
                sh '''
                    mkdir -p /dijitalbelge/dokuman
                    rsync -a --delete --exclude='.git' ./ /dijitalbelge/dokuman/
                '''
            }
        }

        stage('Docker up') {
            steps {
                dir('/dijitalbelge/dokuman') {
                    sh 'docker compose up -d --build'
                }
            }
        }
    }

    post {
        success { echo 'Build ve deploy başarılı.' }
        failure { echo 'Pipeline başarısız oldu.' }
    }
}