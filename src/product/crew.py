from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew
from product.tools.reddit_tool import RedditJSONTool, RedditRSSTool, SerperRedditTool
from product.tools.serper_tool import serper_search
from crewai_tools import WebsiteSearchTool

@CrewBase
class ProductDiscoveryCrew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # -------- Agents --------

    @agent
    def market_landscape_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["market_landscape_agent"],
            tools=[serper_search]  # Web search for competitor research
        )

    @agent
    def customer_pain_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_pain_agent"],
            tools=[
                SerperRedditTool(),      # Google search for Reddit
                RedditJSONTool(),        # Direct Reddit JSON API
                RedditRSSTool()          # Reddit RSS feeds
            ]
        )

    @agent
    def opportunity_sizing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["opportunity_sizing_agent"],
            tools=[
                serper_search,         # Search for market size data
                WebsiteSearchTool()    # Scrape industry sites
            ]
        )

    @agent
    def risk_assumptions_agent(self) -> Agent:
        return Agent(config=self.agents_config["risk_assumptions_agent"])

    @agent
    def strategy_synthesizer_agent(self) -> Agent:
        return Agent(config=self.agents_config["strategy_synthesizer_agent"])

    # -------- Tasks --------

    @task
    def market_landscape_task(self) -> Task:
        return Task(config=self.tasks_config["market_landscape_task"])

    @task
    def subreddit_discovery_task(self) -> Task:
        return Task(config=self.tasks_config["subreddit_discovery_task"])

    @task
    def customer_pain_task(self) -> Task:
        return Task(
            config=self.tasks_config["customer_pain_task"],
            context=[self.subreddit_discovery_task()]  
        )

    @task
    def opportunity_sizing_task(self) -> Task:
        return Task(config=self.tasks_config["opportunity_sizing_task"])

    @task
    def risk_assumptions_task(self) -> Task:
        return Task(config=self.tasks_config["risk_assumptions_task"])

    @task
    def final_strategy_task(self) -> Task:
        return Task(config=self.tasks_config["final_strategy_task"])
        

    # -------- Crew --------

    @crew
    def crew(self) -> Crew:
        """
        Defines the execution order of the product discovery pipeline.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process="sequential",
            verbose=True,
        )
