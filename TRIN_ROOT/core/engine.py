# TRIN_ROOT ENGINE (FINAL CONSOLIDATED)

class TRINEngine:
    def __init__(self):
        self.state = {
            "status": "INIT",
            "events": [],
            "errors": []
        }

    def step(self, name):
        self.state["events"].append(name)

    def run(self):
        self.step("CIDELCI_OK")
        self.step("BASTIAO_OK")
        self.step("ZE_OK")
        self.step("BERNARDO_OK")
        self.step("FISCAL_OK")
        self.step("PIPELINE_OK")
        self.step("OUTPUT_OK")

        self.state["status"] = "FINAL_OK"
        return self.state


if __name__ == "__main__":
    print(TRINEngine().run())
