def get_query(productType: str, after: str = ""):
    return """
        query {
          productType(id: "PRODUCT_TYPE") {
            name
            products(first: 100, after: "AFTER") {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                node {
                  name
                  slug
                  category {
                    name
                    slug
                    parent {
                      name
                      slug
                      parent {
                        name
                        slug
                      }
                    }
                  }
                  attributes {
                    attribute {
                      name
                    }
                    values {
                      name
                    }
                  }
                  pricing {
                    priceRange {
                      start {
                        currency
                        gross {
                          currency
                          amount
                        }
                        net {
                          currency
                          amount
                        }
                        tax {
                          currency
                          amount
                        }
                      }
                      stop {
                        currency
                        gross {
                          currency
                          amount
                        }
                        net {
                          currency
                          amount
                        }
                        tax {
                          currency
                          amount
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """.replace("AFTER", after).replace("PRODUCT_TYPE", productType)
