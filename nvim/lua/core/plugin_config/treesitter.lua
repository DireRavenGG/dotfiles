require'nvim-treesitter.configs'.setup {
  ensure_installed = { 'vim', 'lua', 'javascript', 'typescript', 'html', 'css' },
  sync_install = false, 
  auto_install = true, 
  highlight = {
    enable = true,
  },
}
