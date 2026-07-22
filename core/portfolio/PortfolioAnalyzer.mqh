//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioAnalyzer.mqh                                  |
//| Layer   : Core / Portfolio                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Analyzer                                     |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_PORTFOLIOANALYZER_MQH
#define CORE_PORTFOLIO_PORTFOLIOANALYZER_MQH

#include "PortfolioExposure.mqh"
#include "models/PortfolioSnapshot.mqh"

//--------------------------------------------------

class CPortfolioAnalyzer
{
private:

   CPortfolioExposure m_exposure;

public:

   //--------------------------------------------------

   bool Analyze(
      CPortfolioSnapshot &snapshot)
   {
      if(!m_exposure.Calculate(snapshot))
         return false;

      //--------------------------------------------------
      // Reserved for future analysis
      //
      // - Symbol Correlation
      // - Sector Exposure
      // - Portfolio VaR
      // - Portfolio Risk Score
      // - Diversification Score
      //--------------------------------------------------

      return snapshot.Valid;
   }

   //--------------------------------------------------

   bool IsHealthy()
   {
      CPortfolioSnapshot snapshot;

      if(!Analyze(snapshot))
         return false;

      if(snapshot.TotalExposurePercent > 20.0)
         return false;

      return true;
   }

};

#endif