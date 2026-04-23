class RetornoPainelAdminMixin:
    _parent_admin = None
    _return_view = None

    def _mostrar_painel_admin(self, *, refresh: bool = False) -> None:
        if self._return_view is not None:
            self._return_view.show()
            if refresh and hasattr(self._return_view, "_carregar_painel"):
                self._return_view._carregar_painel()
            return

        if self._parent_admin is not None:
            self._parent_admin.show()
            if refresh and hasattr(self._parent_admin, "_refresh_current_management_page"):
                self._parent_admin._refresh_current_management_page()
            return

        from modules.admin.views.painel_admin_view import PainelAdminView

        self.painel_admin = PainelAdminView()
        self.painel_admin.show()
