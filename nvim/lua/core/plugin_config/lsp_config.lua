require("mason").setup()
require("mason-lspconfig").setup({
  ensure_installed = { "tsserver" },
  automatic_installation = true,
})


local on_attach = function(_,_)
  vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, {}) 
  vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, {})
  
  vim.keymap.set('n', 'gd', vim.lsp.buf.definition, {})
  vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, {})
  vim.keymap.set('n', 'K', vim.lsp.buf.hover, {})
end


require("lspconfig")["tsserver"].setup{
  on_attach = on_attach,
  flags = lsp_flags,
}

