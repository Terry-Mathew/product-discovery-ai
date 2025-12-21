"""
Serper API Tools for Market Research
Uses Serper.dev API for web search (2,500 free searches/month)
"""

from crewai_tools import SerperDevTool

# General web search tool for any agent
serper_search = SerperDevTool()

# You can use this in agents like:
# from product.tools.serper_tool import serper_search
# 
# Agent(tools=[serper_search], ...)
