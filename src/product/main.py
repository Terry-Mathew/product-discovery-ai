from product.crew import ProductDiscoveryCrew

def run():
    """
    Command-line entry point for testing.
    For production, use the Gradio app (app.py or app_basic.py).
    """
    print("\n=== Product Discovery AI - CLI Mode ===\n")
    
    product_idea = input("Product Idea: ").strip()
    target_customer = input("Target Customer: ").strip()
    constraints = input("Constraints (optional, press Enter to skip): ").strip()
    industry = input("Industry (e.g., fintech, healthcare, edtech): ").strip()
    vertical = input("Business Model (e.g., B2C SaaS, B2B Enterprise): ").strip()
    
    if not product_idea or not target_customer:
        print("❌ Error: Product idea and target customer are required.")
        return
    
    inputs = {
        "product_idea": product_idea,
        "target_customer": target_customer,
        "constraints": constraints or "No specific constraints",
        "industry": industry or "Not specified",
        "vertical": vertical or "Not specified"
    }

    print("\n⏳ Running analysis... This may take 3-5 minutes.\n")
    
    crew = ProductDiscoveryCrew().crew()
    result = crew.kickoff(inputs=inputs)
    
    print("\n" + "=" * 80)
    print("FINAL PRODUCT RECOMMENDATION")
    print("=" * 80 + "\n")
    print(result)

if __name__ == "__main__":
    run()
