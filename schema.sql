
CREATE TABLE users (
	id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	username VARCHAR(100) COLLATE utf8_unicode_ci NOT NULL, 
	email VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL, 
	password_hash VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL, 
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)DEFAULT CHARSET=utf8 ENGINE=InnoDB COLLATE utf8_unicode_ci


CREATE UNIQUE INDEX username ON users (username)

CREATE TABLE costs (
	id INTEGER(11) NOT NULL AUTO_INCREMENT, 
	user_id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	vehicle_id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	cf_ipva FLOAT DEFAULT '0', 
	cf_licenciamento FLOAT DEFAULT '0', 
	cf_seguro_obrig FLOAT DEFAULT '0', 
	cf_seguro_carro FLOAT DEFAULT '0', 
	cf_inss FLOAT DEFAULT '155.32', 
	cf_internet FLOAT DEFAULT '60', 
	cv_alim_dia FLOAT DEFAULT '30', 
	cv_lavagem FLOAT DEFAULT '120', 
	preco_comb FLOAT DEFAULT '5.8', 
	consumo_comb FLOAT DEFAULT '10', 
	tipo_comb VARCHAR(50) COLLATE utf8_unicode_ci DEFAULT 'Gasolina', 
	cv_manut_mensal FLOAT DEFAULT '150', 
	cv_oleo FLOAT DEFAULT '250', 
	cv_alinhamento FLOAT DEFAULT '0', 
	cv_pneu FLOAT DEFAULT '1600', 
	cp_iss FLOAT DEFAULT '5', 
	cp_icms FLOAT DEFAULT '0', 
	margem_iss FLOAT DEFAULT '30', 
	PRIMARY KEY (id), 
	CONSTRAINT costs_ibfk_1 FOREIGN KEY(user_id) REFERENCES users (id)
)DEFAULT CHARSET=utf8 ENGINE=InnoDB COLLATE utf8_unicode_ci


CREATE UNIQUE INDEX unique_user_vehicle ON costs (user_id, vehicle_id)

CREATE TABLE profiles (
	user_id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	nome VARCHAR(255) COLLATE utf8_unicode_ci DEFAULT '', 
	email VARCHAR(255) COLLATE utf8_unicode_ci DEFAULT '', 
	whatsapp VARCHAR(50) COLLATE utf8_unicode_ci DEFAULT '', 
	estado VARCHAR(2) COLLATE utf8_unicode_ci DEFAULT '', 
	cidade VARCHAR(255) COLLATE utf8_unicode_ci DEFAULT '', 
	dias_semana INTEGER(11) DEFAULT '6', 
	horas_dia INTEGER(11) DEFAULT '8', 
	km_dia FLOAT DEFAULT '150', 
	veiculo_ativo_id VARCHAR(36) COLLATE utf8_unicode_ci DEFAULT '', 
	PRIMARY KEY (user_id), 
	CONSTRAINT profiles_ibfk_1 FOREIGN KEY(user_id) REFERENCES users (id)
)DEFAULT CHARSET=utf8 ENGINE=InnoDB COLLATE utf8_unicode_ci



CREATE TABLE vehicles (
	id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	user_id VARCHAR(36) COLLATE utf8_unicode_ci NOT NULL, 
	marca VARCHAR(255) COLLATE utf8_unicode_ci DEFAULT '', 
	modelo VARCHAR(255) COLLATE utf8_unicode_ci DEFAULT '', 
	ano VARCHAR(50) COLLATE utf8_unicode_ci DEFAULT '', 
	valor_fipe VARCHAR(100) COLLATE utf8_unicode_ci DEFAULT '', 
	tipo_posse VARCHAR(50) COLLATE utf8_unicode_ci DEFAULT 'Próprio', 
	valor_aluguel_semana FLOAT DEFAULT '0', 
	valor_parcela FLOAT DEFAULT '0', 
	parcelas_restantes INTEGER(11) DEFAULT '0', 
	PRIMARY KEY (id), 
	CONSTRAINT vehicles_ibfk_1 FOREIGN KEY(user_id) REFERENCES users (id)
)DEFAULT CHARSET=utf8 ENGINE=InnoDB COLLATE utf8_unicode_ci


CREATE INDEX user_id ON vehicles (user_id)