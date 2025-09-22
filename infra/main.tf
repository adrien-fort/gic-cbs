# Terraform and AKS deployment starter (pseudo)
# You will need to fill in Azure credentials, resource group, and other details.

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "gic_cbs" {
  name     = "gic-cbs-rg"
  location = "East US"
}

resource "azurerm_kubernetes_cluster" "gic_cbs_aks" {
  name                = "gic-cbs-aks"
  location            = azurerm_resource_group.gic_cbs.location
  resource_group_name = azurerm_resource_group.gic_cbs.name
  dns_prefix          = "gic-cbs"

  default_node_pool {
    name       = "default"
    node_count = 1
  vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }
}

# You would also need to add Azure Container Registry, role assignments, and output values for kubeconfig, etc.
# See Azure Terraform docs for full production setup.
