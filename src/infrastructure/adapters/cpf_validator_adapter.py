import json
import logging

import boto3
from botocore.exceptions import ClientError

from src.infrastructure.config.settings import settings
from src.infrastructure.observability.telemetry import record_integration_error

logger = logging.getLogger(__name__)


class CpfValidatorAdapter:
    """Adapter to call the CPF validator Lambda function."""

    def __init__(self, lambda_arn: str = None, region_name: str = None):
        self.lambda_arn = lambda_arn or settings.CPF_VALIDATOR_LAMBDA_ARN
        self.region_name = region_name or settings.AWS_REGION
        self._lambda_client = None

    @property
    def lambda_client(self):
        """Lazy initialization of Lambda client."""
        if self._lambda_client is None:
            self._lambda_client = boto3.client("lambda", region_name=self.region_name)
        return self._lambda_client

    def validate_cpf(self, cpf: str) -> bool:
        """
        Validate CPF using the Lambda function.

        Args:
            cpf: The CPF string to validate

        Returns:
            bool: True if CPF is valid, False otherwise
        """
        # Skip validation if Lambda ARN is not configured (for local development)
        if not self.lambda_arn:
            # Fall back to local validation for development
            from src.domain.value_objects.cpf_cnpj import CpfCnpj

            try:
                CpfCnpj(cpf)
                return True
            except Exception:
                return False

        try:
            # Prepare the payload for Lambda invocation
            payload = {"cpf": cpf}

            # Invoke the Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_arn,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            # Parse the response
            response_payload = json.loads(response["Payload"].read())
            return response_payload.get("valid", False)

        except ClientError as e:
            logger.error(f"Failed to invoke CPF validator Lambda: {e}")
            record_integration_error("cpf_validator_lambda", "validate_cpf", e)
            # In case of error, fall back to local validation for resilience
            # Or could raise an exception depending on requirements
            from src.domain.value_objects.cpf_cnpj import CpfCnpj

            try:
                CpfCnpj(cpf)
                return True
            except Exception:
                return False
        except Exception as e:
            logger.error(f"Unexpected error in CPF validation: {e}")
            record_integration_error("cpf_validator_lambda", "validate_cpf", e)
            # Fall back to local validation
            from src.domain.value_objects.cpf_cnpj import CpfCnpj

            try:
                CpfCnpj(cpf)
                return True
            except Exception:
                return False
