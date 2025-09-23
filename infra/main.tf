# Terraform and AKS deployment starter (pseudo)
# You will need to fill in Azure credentials, resource group, and other details.

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "gic_cbs" {
  name     = "gic-cbs-rg"
  location = "southeastasia"
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

resource "azurerm_container_registry" "gic_cbs_acr" {
  name                = "giccbsacrmain"
  resource_group_name = azurerm_resource_group.gic_cbs.name
  location            = azurerm_resource_group.gic_cbs.location
  sku                 = "Basic"
  admin_enabled       = true
}



output "acr_login_server" {
  value = azurerm_container_registry.gic_cbs_acr.login_server
}
output "acr_admin_username" {
  value = azurerm_container_registry.gic_cbs_acr.admin_username
}
output "acr_admin_password" {
  value     = azurerm_container_registry.gic_cbs_acr.admin_password
  sensitive = true
}

# You would also need to add role assignments, and output values for kubeconfig, etc.
# See Azure Terraform docs for full production setup.
