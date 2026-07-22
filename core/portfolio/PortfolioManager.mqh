//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioManager.mqh                                   |
//| Layer   : Core / Portfolio                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Manager                                      |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_PORTFOLIOMANAGER_MQH
#define CORE_PORTFOLIO_PORTFOLIOMANAGER_MQH

#include "PortfolioAllocator.mqh"
#include "PortfolioAnalyzer.mqh"
#include "PortfolioExposure.mqh"

#include "models/PortfolioSnapshot.mqh"

//--------------------------------------------------

class CPortfolioManager
{
private:

   CPortfolioExposure m_exposure;

   CPortfolioAnalyzer m_analyzer;

   CPortfolioAllocator m_allocator;

public:

   //--------------------------------------------------

   bool Refresh(
      CPortfolioSnapshot &snapshot)
   {
      return m_exposure.Calculate(snapshot);
   }

   //--------------------------------------------------

   bool Analyze(
      CPortfolioSnapshot &snapshot)
   {
      return m_analyzer.Analyze(snapshot);
   }

   //--------------------------------------------------

   bool CanOpenNewPosition()
   {
      CPortfolioSnapshot snapshot;

      if(!Analyze(snapshot))
         return false;

      return m_allocator.Allocate(snapshot);
   }

   //--------------------------------------------------

   double RecommendedRiskPercent()
   {
      return m_allocator.RecommendedRiskPercent();
   }

   //--------------------------------------------------

   CPortfolioSnapshot GetSnapshot()
   {
      CPortfolioSnapshot snapshot;

      Refresh(snapshot);

      return snapshot;
   }

};

#endif