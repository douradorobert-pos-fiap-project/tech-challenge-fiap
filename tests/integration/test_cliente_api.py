import uuid


class TestAuth:
    def test_login_sucesso(self, client) -> None:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "secret"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_credenciais_invalidas(self, client) -> None:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_me_com_token_valido(self, client, auth_headers) -> None:
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["user"] == "admin"

    def test_me_sem_token(self, client) -> None:
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestClienteApi:
    def test_criar_cliente_com_sucesso(self, client, auth_headers) -> None:
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
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Joao Silva"
        assert data["cpf_cnpj"] == "52998224725"
        assert data["ativo"] is True

    def test_criar_cliente_cnpj(self, client, auth_headers) -> None:
        response = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Empresa XYZ",
                "cpf_cnpj": "11444777000161",
                "email": "contato@xyz.com",
                "telefone": "1133333333",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["cpf_cnpj"] == "11444777000161"

    def test_criar_cliente_cpf_invalido(self, client, auth_headers) -> None:
        response = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "11111111111",
                "email": "joao@example.com",
                "telefone": "11999999999",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_criar_cliente_sem_auth(self, client) -> None:
        response = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "52998224725",
                "email": "joao@example.com",
                "telefone": "11999999999",
            },
        )
        assert response.status_code == 401

    def test_listar_clientes(self, client, auth_headers) -> None:
        client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "52998224725",
                "email": "joao@ex.com",
                "telefone": "111",
            },
            headers=auth_headers,
        )
        response = client.get("/api/v1/clientes", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_obter_cliente_por_id(self, client, auth_headers) -> None:
        create = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "52998224725",
                "email": "joao@ex.com",
                "telefone": "111",
            },
            headers=auth_headers,
        )
        cliente_id = create.json()["id"]
        response = client.get(f"/api/v1/clientes/{cliente_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nome"] == "Joao"

    def test_obter_cliente_inexistente(self, client, auth_headers) -> None:
        response = client.get(f"/api/v1/clientes/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    def test_atualizar_cliente(self, client, auth_headers) -> None:
        create = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "52998224725",
                "email": "joao@ex.com",
                "telefone": "111",
            },
            headers=auth_headers,
        )
        cliente_id = create.json()["id"]
        response = client.put(
            f"/api/v1/clientes/{cliente_id}",
            json={"nome": "Joao Santos"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Joao Santos"

    def test_deletar_cliente(self, client, auth_headers) -> None:
        create = client.post(
            "/api/v1/clientes",
            json={
                "nome": "Joao",
                "cpf_cnpj": "52998224725",
                "email": "joao@ex.com",
                "telefone": "111",
            },
            headers=auth_headers,
        )
        cliente_id = create.json()["id"]
        response = client.delete(f"/api/v1/clientes/{cliente_id}", headers=auth_headers)
        assert response.status_code == 204
