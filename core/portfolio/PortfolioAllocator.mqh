//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioAllocator.mqh                                 |
//| Layer   : Core / Portfolio                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Allocation Manager                           |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_PORTFOLIOALLOCATOR_MQH
#define CORE_PORTFOLIO_PORTFOLIOALLOCATOR_MQH

#include "PortfolioAnalyzer.mqh"
#include "models/PortfolioSnapshot.mqh"

//--------------------------------------------------

class CPortfolioAllocator
{
private:

   CPortfolioAnalyzer m_analyzer;

public:

   //--------------------------------------------------

   bool Allocate(
      CPortfolioSnapshot &snapshot)
   {
      if(!m_analyzer.Analyze(snapshot))
         return false;

      //--------------------------------------------------
      // Phase 1 Allocation Rules
      //--------------------------------------------------

      if(snapshot.TotalExposurePercent >= 20.0)
         return false;

      return true;
   }

   //--------------------------------------------------

   double RecommendedRiskPercent()
   {
      CPortfolioSnapshot snapshot;

      if(!m_analyzer.Analyze(snapshot))
         return 0.0;

      if(snapshot.TotalExposurePercent < 5.0)
         return 1.00;

      if(snapshot.TotalExposurePercent < 10.0)
         return 0.75;

      if(snapshot.TotalExposurePercent < 15.0)
         return 0.50;

      if(snapshot.TotalExposurePercent < 20.0)
         return 0.25;

      return 0.0;
   }

};

#endif