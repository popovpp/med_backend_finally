CREATE TABLE "public.documents_types" (
	"id" serial NOT NULL,
	"client_document_type_id" integer NOT NULL,
	"name" varchar(200) NOT NULL UNIQUE,
	"description" varchar(500) NOT NULL,
	"document_params" json NOT NULL,
	"is_online_allowed" bool NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "documents_types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_documents" (
	"id" serial NOT NULL,
	"user_id" integer NOT NULL,
	"document_type_id" integer NOT NULL,
	"request_date" DATE NOT NULL,
	"is_needed_paper_original" bool NOT NULL,
	"status" integer NOT NULL,
	"document_url" varchar(200) NOT NULL,
	"description" varchar(500) NOT NULL,
	"is_active" integer NOT NULL,
	CONSTRAINT "users_documents_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users" (
	"id" serial NOT NULL,
	"client_card_id" integer UNIQUE DEFAULT 'null',
	"first_name" varchar(100) NOT NULL,
	"last_name" varchar(100) NOT NULL,
	"patronymic" varchar(100) DEFAULT 'null',
	"birth_date" DATE NOT NULL,
	"gender" varchar(1) DEFAULT 'null',
	"email" varchar(100) NOT NULL UNIQUE,
	"phone_number" varchar(20) NOT NULL UNIQUE,
	"additional_phone_number" varchar(20) DEFAULT 'null',
	"password" varchar(200) DEFAULT 'null',
	"is_active" bool NOT NULL DEFAULT 'true',
	"is_verified" bool NOT NULL DEFAULT 'false',
	"created" DATE NOT NULL,
	"last_login" DATE,
	"last_visit" DATE,
	"city_id" integer NOT NULL,
	"address" varchar(200) NOT NULL,
	"longitude" float4,
	"latitude" float4,
	"inn" varchar(20),
	"snils" varchar(20),
	"default_medical_center_id" integer,
	CONSTRAINT "users_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);




ALTER TABLE "users_documents" ADD CONSTRAINT "users_documents_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_documents" ADD CONSTRAINT "users_documents_fk1" FOREIGN KEY ("document_type_id") REFERENCES "documents_types"("id");

ALTER TABLE "users" ADD CONSTRAINT "users_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");
ALTER TABLE "users" ADD CONSTRAINT "users_fk1" FOREIGN KEY ("default_medical_center_id") REFERENCES "medical_centers"("id");




