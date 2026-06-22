import uuid


class TestVeiculoApi:
    def _criar_cliente(self, client, auth_headers) -> str:
        response = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao Silva",
                "cpf_cnpj": "52998224725",
                "email": "joao@example.com",
                "telefone": "11999999999",
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_criar_veiculo(self, client, auth_headers) -> None:
        cliente_id = self._criar_cliente(client, auth_headers)
        response = client.post(
            "/api/v1/veiculos",
            json={
                "cliente_id": cliente_id,
                "placa": "ABC1D23",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["placa"] == "ABC1D23"

    def test_criar_veiculo_placa_invalida(self, client, auth_headers) -> None:
        cliente_id = self._criar_cliente(client, auth_headers)
        response = client.post(
            "/api/v1/veiculos",
            json={
                "cliente_id": cliente_id,
                "placa": "INVALID",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_listar_veiculos(self, client, auth_headers) -> None:
        cliente_id = self._criar_cliente(client, auth_headers)
        client.post(
            "/api/v1/veiculos",
            json={
                "cliente_id": cliente_id,
                "placa": "ABC1D23",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
            },
            headers=auth_headers,
        )
        response = client.get("/api/v1/veiculos", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestServicoApi:
    def test_criar_servico(self, client, auth_headers) -> None:
        response = client.post(
            "/api/v1/servicos",
            json={"nome": "Troca de Oleo", "descricao": "Troca de oleo e filtro", "preco_base": 80.00},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["preco_base"] == 80.00

    def test_listar_servicos(self, client, auth_headers) -> None:
        client.post(
            "/api/v1/servicos",
            json={"nome": "Troca de Oleo", "descricao": "", "preco_base": 80.00},
            headers=auth_headers,
        )
        response = client.get("/api/v1/servicos", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestPecaApi:
    def test_criar_peca(self, client, auth_headers) -> None:
        response = client.post(
            "/api/v1/pecas",
            json={
                "nome": "Filtro de Oleo",
                "sku": "FO-001",
                "preco": 25.50,
                "quantidade_estoque": 20,
                "estoque_minimo": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["sku"] == "FO-001"

    def test_ajustar_estoque(self, client, auth_headers) -> None:
        create = client.post(
            "/api/v1/pecas",
            json={
                "nome": "Filtro",
                "sku": "FO-001",
                "preco": 25.00,
                "quantidade_estoque": 20,
                "estoque_minimo": 5,
            },
            headers=auth_headers,
        )
        peca_id = create.json()["id"]
        response = client.patch(
            f"/api/v1/pecas/{peca_id}/estoque",
            json={"nova_quantidade": 50},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["quantidade_estoque"] == 50
