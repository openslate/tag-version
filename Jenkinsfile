@Library('OpenSlateProd')_  // https://github.com/openslate/jenkins-shared-library

def customPublishFunction = {
    sh "compose-flow -e ${env.DEPLOY_ENV} --project-name ${env.REPO_NAME} compose run --rm app /bin/bash ./scripts/publish.sh"
}

def publishWhen = { env.TAG_NAME }

openslatePipeline {
    mentions = '@roberto <@marcusian>'
    deployEnv = 'prod'
    lint = true
    test = true
    publish = publishWhen
    publishFunction = customPublishFunction
    deploy = false
}
