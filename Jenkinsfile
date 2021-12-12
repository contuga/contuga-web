pipeline {
    agent {
        docker {
          image 'circleci/python:3.8-browsers'
          args '-u root --privileged'
        }
    }

    stages {
        stage('Setup') {
          steps {
            sh 'pip install pipenv'
            sh 'pipenv sync --dev'
          }
        }
        stage('Test') {
          steps {
            sh 'pipenv run coverage run manage.py test'
            sh 'pipenv run coverage report'
            sh 'pipenv run coverage html'
          }
        }
        stage('Format') {
          steps {
            sh 'pipenv run black . --check'
          }
        }
    }
}
