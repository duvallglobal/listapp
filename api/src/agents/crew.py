from crewai import Agent, Task, Crew
from langchain.llms import OpenAI
from .vision_agent import VisionAgent
from .marketplace_agent import MarketplaceAgent
from .pricing_agent import PricingAgent
from .recommendation_agent import RecommendationAgent

class ProductAnalysisCrew:
    def __init__(self, api_keys, cache_service):
        self.api_keys = api_keys
        self.cache_service = cache_service
        self.llm = OpenAI(temperature=0.2)
        
    def create_crew(self):
        # Create specialized agents
        vision_agent = Agent(
            role="Vision Analysis Expert",
            goal="Accurately identify and describe products from images",
            backstory="You are an expert in computer vision and product identification",
            verbose=True,
            llm=self.llm,
            tools=[VisionAgent(self.api_keys).get_tools()]
        )
        
        marketplace_agent = Agent(
            role="Marketplace Research Specialist",
            goal="Find accurate pricing and market data for products",
            backstory="You are a market research expert with deep knowledge of online marketplaces",
            verbose=True,
            llm=self.llm,
            tools=[MarketplaceAgent(self.api_keys).get_tools()]
        )
        
        pricing_agent = Agent(
            role="Pricing Strategist",
            goal="Determine optimal pricing strategy for maximum profit",
            backstory="You are a pricing expert who understands market dynamics",
            verbose=True,
            llm=self.llm,
            tools=[PricingAgent().get_tools()]
        )
        
        recommendation_agent = Agent(
            role="Platform Recommendation Expert",
            goal="Recommend the best selling platform for each product",
            backstory="You understand the fees, audience, and dynamics of every online marketplace",
            verbose=True,
            llm=self.llm,
            tools=[RecommendationAgent().get_tools()]
        )
        
        # Create the crew
        crew = Crew(
            agents=[vision_agent, marketplace_agent, pricing_agent, recommendation_agent],
            tasks=[
                Task(
                    description="Analyze this product image and provide complete details",
                    agent=vision_agent
                ),
                Task(
                    description="Research current market prices and demand for this product",
                    agent=marketplace_agent
                ),
                Task(
                    description="Determine optimal pricing strategy across platforms",
                    agent=pricing_agent
                ),
                Task(
                    description="Recommend the best platform for selling this product",
                    agent=recommendation_agent
                )
            ],
            verbose=True
        )
        
        return crew
    
    def analyze_product(self, image_data, user_input=None):
        """
        Orchestrate the full product analysis workflow
        """
        crew = self.create_crew()
        result = crew.kickoff(inputs={"image_data": image_data, "user_input": user_input})
        
        # Cache results
        self.cache_service.store_analysis(result)
        
        return result
