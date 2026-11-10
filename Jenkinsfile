pipeline {
    agent { label 'name1' }

    environment {
        HARBOR_REGISTRY = 'harbor.fullcheck.app'
        HARBOR_PROJECT  = 'dijitalbelge'
        IMAGE_NAME      = 'dokuman2'
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        IMAGE_REPO      = "${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${IMAGE_NAME}"
        NAMESPACE       = 'dijitalbelge'
    }

    options {
        quietPeriod(30)
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

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

        stage('Build image') {
            steps {
                sh 'docker build --pull -t $IMAGE_REPO:$IMAGE_TAG -t $IMAGE_REPO:latest .'
                stash name: 'k8s', includes: 'k8s/**'
            }
        }

        stage('Push to Harbor') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'harbor-credentials',
                    usernameVariable: 'HARBOR_USER',
                    passwordVariable: 'HARBOR_PASS'
                )]) {
                    retry(3) {
                        sh '''
                            echo "$HARBOR_PASS" | docker login $HARBOR_REGISTRY -u "$HARBOR_USER" --password-stdin
                            docker push $IMAGE_REPO:$IMAGE_TAG
                            docker push $IMAGE_REPO:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            agent { label 'vps2' }
            steps {
                unstash 'k8s'
                sh '''
                    export KUBECONFIG="$HOME/.kube/config"
                    kubectl -n $NAMESPACE get namespace >/dev/null
                    sed -i 's|newTag:.*|newTag: "'"$IMAGE_TAG"'"|' k8s/kustomization.yaml
                    kubectl apply -k k8s/
                    kubectl -n $NAMESPACE rollout status deployment/dijitalbelge-docs --timeout=5m
                '''
            }
        }
    }

    post {
        success {
            echo "Dokümantasyon ${IMAGE_TAG} sürümü Kubernetes'e gönderildi."
            sh 'docker image prune -f || true'
        }
        failure {
            echo 'Pipeline başarısız. vps2 ajanında kubectl erişimini ve Jenkins Harbor/GitHub credential ayarlarını kontrol edin.'
        }
    }
}
