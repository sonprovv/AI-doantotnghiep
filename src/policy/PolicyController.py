class PolicyController:
    
    def __init__(self):
        from src.policy.PolicyService import PolicyService
        self.policyService = PolicyService()

    def answer(self, query: str, reference: dict):
        result = self.policyService.policy_answer(query)
        return result
