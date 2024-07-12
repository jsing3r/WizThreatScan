"""
Python 3.6+
pip(3) install requests
"""
import base64
import json
import requests
import os

# variables
debugMode = False
path = './ConnectorList.txt'

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

CLIENT_ID = "wgxq75hrlndpbktx3eupevf2x3qaui7fv5fvo5fomrfgupdwaechg"
CLIENT_SECRET = "YZnAOXyJWm01h9vaUOMj37dsyarFvwyqe0i4dfJdCQryJEMh7LfU8GDupkw5qaOw"

# Uncomment the following section to define the proxies in your environment,
#   if necessary:
# http_proxy  = "http://"+user+":"+passw+"@x.x.x.x:abcd"
# https_proxy = "https://"+user+":"+passw+"@y.y.y.y:abcd"
# proxyDict = {
#     "http"  : http_proxy,
#     "https" : https_proxy
# }

# The GraphQL query that defines which data you wish to fetch.
QUERY = """
    query DeploymentsPageTable($after: String, $first: Int, $filterBy: DeploymentFilters) {
      deployments(after: $after, first: $first, filterBy: $filterBy) {
        nodes {
          deploymentSources(first: $first) {
            nodes {
              ...DeploymentSourceDetails
            }
            totalCount
          }
          ...DeploymentPageDetails
          childDeployments(first: 5) {
            nodes {
              deploymentSources(first: $first) {
                nodes {
                  ...DeploymentSourceDetails
                }
              }
              ...DeploymentPageDetails
              childDeployments(first: 5) {
                nodes {
                  deploymentSources(first: $first) {
                    nodes {
                      ...DeploymentSourceDetails
                    }
                  }
                  ...DeploymentPageDetails
                  childDeployments(first: 5) {
                    nodes {
                      deploymentSources(first: $first) {
                        nodes {
                          ...DeploymentSourceDetails
                        }
                      }
                      ...DeploymentPageDetails
                    }
                    totalCount
                  }
                }
                totalCount
              }
            }
            totalCount
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
        totalCount
      }
    }
    
        fragment DeploymentSourceDetails on DeploymentSource {
      ... on CloudAccount {
        id
        name
        lastScannedAt
        cloudProvider
      }
      ... on KubernetesCluster {
        id
        name
        kind
        lastSeenAt: lastScannedAt
      }
      ... on ContainerRegistry {
        id
        name
      }
      ... on CloudOrganization {
        id
        name
        cloudProvider
      }
      ... on Repository {
        id
        name
      }
    }
    

        fragment DeploymentPageDetails on Deployment {
      id
      name
      type
      status
      lastSeenAt
      modules
      object {
        ... on Connector {
          id
          name
          enabled
          status
          type {
            id
            name
          }
          outpost {
            id
            name
          }
          connectorConfig: config {
            ... on ConnectorConfigKubernetes {
              isOnPrem
            }
          }
          extraConfig
          lastActivity
          enabled
          createdAt
          createdBy {
            ... on User {
              id
              email
              name
            }
            ... on Connector {
              id
              name
            }
          }
        }
        ... on AdmissionController {
          id
          healthStatus
          cluster {
            name
          }
          lastSeen
        }
        ... on Outpost {
          ...DeploymentsPageTableOutpost
        }
        ... on OutpostCluster {
          id
          httpProxyConfig {
            httpProxyURL
            httpsProxyURL
            vpcCIDRs
          }
          nodeGroups {
            nodeGroupId
            type
            maxNodeCount
            minNodeCount
          }
          createdAt
          clusterOutpost: outpost {
            id
            serviceType
            inAccountOutpostType
            externalInternetAccess
            selfManagedConfig {
              imagePullSecret
            }
            managedConfig {
              manualNetwork
            }
          }
          config {
            ... on OutpostClusterAWSConfig {
              clusterName
            }
            ... on OutpostClusterAzureConfig {
              clusterName
              serviceAuthorizedIPRanges
            }
            ... on OutpostClusterGCPConfig {
              clusterName
            }
            ... on OutpostClusterOCIConfig {
              clusterName
            }
            ... on OutpostClusterAlibabaConfig {
              clusterName
            }
          }
          outpostClusterServiceType: serviceType
          addedBy {
            id
            name
          }
        }
        ... on SensorGroup {
          id
          sensorGroupType: type
          graphEntity {
            id
            type
            name
          }
          sensors(first: 0) {
            totalCount
          }
        }
        ... on Broker {
          id
          name
        }
        ... on RemediationAndResponseDeployment {
          id
          name
          config {
            ... on RemediationAndResponseDeploymentAwsConfig {
              __typename
            }
          }
        }
      }
      subtype {
        ... on OutpostSubType {
          outpostType: type
        }
        ... on OutpostClusterSubType {
          outpostType: type
        }
        ... on KubernetesConnectorSubType {
          kubernetesConnectorType: type
        }
      }
      version
      criticalSystemHealthIssueCount
      highSystemHealthIssueCount
      mediumSystemHealthIssueCount
      lowSystemHealthIssueCount
      informationalSystemHealthIssueCount
    }
    

        fragment DeploymentsPageTableOutpost on Outpost {
      id
      name
      enabled
      createdAt
      outpostStatus: status
      inAccountOutpostType
      selfManaged
      serviceType
      selfManagedConfig {
        version {
          id
        }
      }
      config {
        ... on OutpostAzureConfig {
          environment
          workerID
          orchestratorConfig {
            managedIdentityEnabled
          }
        }
      }
      clusters {
        id
        region
        config {
          ... on OutpostClusterAzureConfig {
            serviceAuthorizedIPRanges
          }
        }
      }
      addedBy {
        id
        name
      }
    }
"""

# The variables sent along with the above query
VARIABLES = {
  "first": 500,
  "filterBy": {
    "status": [
      "ENABLED"
    ],
    "cloudProvider": [
      "AWS",
      "Azure"
    ],
    "type": [
      "CLOUD_CONNECTOR"
    ]
  }
}

def query_wiz_api(query, variables, dc):
    """Query Wiz API for the given query data schema"""

    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url=f"https://api.{dc}.app.wiz.io/graphql",
        #                        json=data, headers=HEADERS, proxies=proxyDict, timeout=180)
        result = requests.post(url=f"https://api.{dc}.app.wiz.io/graphql",
                               json=data, headers=HEADERS, timeout=180)

    except requests.exceptions.HTTPError as e:
        print(f"<p>Wiz-API-Error (4xx/5xx): {str(e)}</p>")
        return e

    except requests.exceptions.ConnectionError as e:
        print(f"<p>Network problem (DNS failure, refused connection, etc): {str(e)}</p>")
        return e

    except requests.exceptions.Timeout as e:
        print(f"<p>Request timed out: {str(e)}</p>")
        return e

    return result.json()


def request_wiz_api_token(client_id, client_secret):
    """Retrieve an OAuth access token to be used against Wiz API"""

    auth_payload = {
      'grant_type': 'client_credentials',
      'audience': 'wiz-api',
      'client_id': client_id,
      'client_secret': client_secret
    }
    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # response = requests.post(url="https://auth.app.wiz.io/oauth/token",
        #                         headers=HEADERS_AUTH, data=auth_payload,
        #                         proxies=proxyDict, timeout=180)
        response = requests.post(url="https://auth.app.wiz.io/oauth/token",
                                headers=HEADERS_AUTH, data=auth_payload, timeout=180)

    except requests.exceptions.HTTPError as e:
        print(f"<p>Error authenticating to Wiz (4xx/5xx): {str(e)}</p>")
        return e

    except requests.exceptions.ConnectionError as e:
        print(f"<p>Network problem (DNS failure, refused connection, etc): {str(e)}</p>")
        return e

    except requests.exceptions.Timeout as e:
        print(f"<p>Request timed out: {str(e)}</p>")
        return e

    try:
        response_json = response.json()
        token = response_json.get('access_token')
        if not token:
            message = f"Could not retrieve token from Wiz: {response_json.get('message')}"
            raise ValueError(message)
    except ValueError as exception:
        message = f"Could not parse API response {exception}. Check Service Account details " \
                    "and variables"
        raise ValueError(message) from exception

    response_json_decoded = json.loads(
        base64.standard_b64decode(pad_base64(token.split(".")[1]))
    )

    response_json_decoded = json.loads(
        base64.standard_b64decode(pad_base64(token.split(".")[1]))
    )
    dc = response_json_decoded["dc"]

    return token, dc


def pad_base64(data):
    """Makes sure base64 data is padded"""
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)
    return data

def readControlList():
    content = ""

    if os.path.isfile(path):
       file = open(path,'r')
       content = file.read(20)
       if debugMode: print("Read file content [", content,"]")
       file.close()
    else:
       if debugMode: print('File not found')

    return content

def openConnectorList():
    file = open(path,'w')

    return file

def writeConnectorList(file, data):

    try:
        file.write(data + '\n')
        if debugMode: print("Wrote file content [", data,"]")
        return True

    except TypeError as e:
        print('Error when writing to file: ', e)
        return False

def closeConnectorList(file):
    file.close()

def main():
    """Main function"""

    print("Getting token.")
    token, dc = request_wiz_api_token(CLIENT_ID, CLIENT_SECRET)
    HEADERS["Authorization"] = "Bearer " + token

    result = query_wiz_api(QUERY, VARIABLES, dc)
    #print(result)  # your data is here!
    #print(json.dumps(result, indent=4, sort_keys=True))
    
    totalCount = result['data']['deployments']['totalCount']
    print("total count", totalCount)

    file = openConnectorList()

    for i in range (0,totalCount,1):
        if debugMode: print("i", i)
        id  = result['data']['deployments']['nodes'][i]['id']
        name = result['data']['deployments']['nodes'][i]['name']
        
        # Testing - dump ID and name, but desired is ID only
        #data = id
        #sdata = ",".join(data)
        sdata = id
        if debugMode: print(sdata)
        writeConnectorList(file, sdata)
    
    closeConnectorList(file)

if __name__ == '__main__':
    main()

