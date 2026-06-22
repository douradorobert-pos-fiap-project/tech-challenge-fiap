import uuid


class TestOrdemServicoApi:
    def _setup_dados_base(self, client, auth_headers) -> dict[str, str]:
        cliente = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao Silva",
                "cpf_cnpj": "52998224725",
                "email": "joao@example.com",
                "telefone": "11999999999",
            },
            headers=auth_headers,
        ).json()

        veiculo = client.post(
            "/api/v1/veiculos",
            json={
                "cliente_id": cliente["id"],
                "placa": "ABC1D23",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
            },
            headers=auth_headers,
        ).json()

        servico1 = client.post(
            "/api/v1/servicos",
            json={"nome": "Troca de Oleo", "descricao": "Troca", "preco_base": 80.00},
            headers=auth_headers,
        ).json()

        servico2 = client.post(
            "/api/v1/servicos",
            json={"nome": "Alinhamento", "descricao": "Alinhamento", "preco_base": 120.00},
            headers=auth_headers,
        ).json()

        peca1 = client.post(
            "/api/v1/pecas",
            json={
                "nome": "Filtro de Oleo",
                "sku": "FO-001",
                "preco": 25.50,
                "quantidade_estoque": 20,
            },
            headers=auth_headers,
        ).json()

        return {
            "cliente_id": cliente["id"],
            "veiculo_id": veiculo["id"],
            "servico1_id": servico1["id"],
            "servico2_id": servico2["id"],
            "peca1_id": peca1["id"],
        }

    def test_abrir_os_com_sucesso(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        response = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [
                    {"servico_id": dados["servico1_id"]},
                    {"servico_id": dados["servico2_id"]},
                ],
                "pecas": [
                    {"peca_id": dados["peca1_id"], "quantidade": 2},
                ],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "AGUARDANDO_APROVACAO"
        assert len(data["orcamento"]["itens_servico"]) == 2
        assert len(data["orcamento"]["itens_peca"]) == 1
        assert data["orcamento"]["total"] == 251.00  # 80+120 + 25.50*2=51

    def test_abrir_os_sem_auth(self, client) -> None:
        response = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": str(uuid.uuid4()),
                "veiculo_id": str(uuid.uuid4()),
                "servicos": [],
                "pecas": [],
            },
        )
        assert response.status_code == 401

    def test_consulta_publica_status(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        response = client.get(f"/api/v1/public/ordens-servico/{os['id']}/status")
        assert response.status_code == 200
        assert response.json()["status"] == "AGUARDANDO_APROVACAO"

    def test_consulta_publica_inexistente(self, client) -> None:
        response = client.get(f"/api/v1/public/ordens-servico/{uuid.uuid4()}/status")
        assert response.status_code == 404

    def test_aprovar_orcamento(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        response = client.post(
            f"/api/v1/ordens-servico/{os['id']}/orcamento/aprovar",
            json={"acao": "APROVAR"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "EM_EXECUCAO"
        assert response.json()["orcamento"]["aprovado"] is True

    def test_recusar_orcamento(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        response = client.post(
            f"/api/v1/ordens-servico/{os['id']}/orcamento/aprovar",
            json={"acao": "RECUSAR"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "CANCELADA"

    def test_aprovar_orcamento_sem_auth(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        response = client.post(
            f"/api/v1/ordens-servico/{os['id']}/orcamento/aprovar",
            json={"acao": "APROVAR"},
        )
        assert response.status_code == 200

    def test_listar_os_ordenacao(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)

        os1 = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        os2 = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico2_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        client.post(
            f"/api/v1/ordens-servico/{os1['id']}/orcamento/aprovar",
            json={"acao": "APROVAR"},
        )

        response = client.get("/api/v1/ordens-servico", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["status"] == "EM_EXECUCAO"
        assert data[1]["status"] == "AGUARDANDO_APROVACAO"

    def test_listar_os_exclui_finalizadas(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os1 = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        client.post(
            f"/api/v1/ordens-servico/{os1['id']}/orcamento/aprovar",
            json={"acao": "APROVAR"},
        )

        client.patch(
            f"/api/v1/ordens-servico/{os1['id']}/status",
            json={"novo_status": "FINALIZADA"},
            headers=auth_headers,
        )

        response = client.get("/api/v1/ordens-servico", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_detalhar_os(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [{"peca_id": dados["peca1_id"], "quantidade": 3}],
            },
            headers=auth_headers,
        ).json()

        response = client.get(f"/api/v1/ordens-servico/{os['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["orcamento"]["total"] == 156.50  # 80 + 25.50*3=76.50

    def test_atualizar_status_valido(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        client.post(
            f"/api/v1/ordens-servico/{os['id']}/orcamento/aprovar",
            json={"acao": "APROVAR"},
        )

        response = client.patch(
            f"/api/v1/ordens-servico/{os['id']}/status",
            json={"novo_status": "FINALIZADA"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "FINALIZADA"

    def test_atualizar_status_invalido(self, client, auth_headers) -> None:
        dados = self._setup_dados_base(client, auth_headers)
        os = client.post(
            "/api/v1/ordens-servico",
            json={
                "cliente_id": dados["cliente_id"],
                "veiculo_id": dados["veiculo_id"],
                "servicos": [{"servico_id": dados["servico1_id"]}],
                "pecas": [],
            },
            headers=auth_headers,
        ).json()

        response = client.patch(
            f"/api/v1/ordens-servico/{os['id']}/status",
            json={"novo_status": "FINALIZADA"},
            headers=auth_headers,
        )
        assert response.status_code == 400
