provider "aws" {
  region = "us-east-1"
}

resource "aws_db_instance" "chatbot_postgres" {
  identifier = "chatbot-db"
  allocated_storage = 20
  engine = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"
  username = "chatbot"
  password = "secretpassword"
  skip_final_snapshot = true
}
