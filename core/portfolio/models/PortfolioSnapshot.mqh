//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioSnapshot.mqh                                  |
//| Layer   : Core / Portfolio / Models                              |
//| Version : 1.1.0                                                  |
//| Purpose : Portfolio Snapshot                                     |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_MODELS_PORTFOLIOSNAPSHOT_MQH
#define CORE_PORTFOLIO_MODELS_PORTFOLIOSNAPSHOT_MQH


class CPortfolioSnapshot
{
public:

   bool Valid;

   int TotalPositions;

   double TotalVolume;

   double TotalExposure;

   double TotalExposurePercent;

   double TotalFloatingProfit;

   double Balance;

   double Equity;

   double Margin;

   double FreeMargin;


public:


   CPortfolioSnapshot()
   {
      Reset();
   }



   void Reset()
   {
      Valid = false;

      TotalPositions = 0;

      TotalVolume = 0.0;

      TotalExposure = 0.0;

      TotalExposurePercent = 0.0;

      TotalFloatingProfit = 0.0;

      Balance = 0.0;

      Equity = 0.0;

      Margin = 0.0;

      FreeMargin = 0.0;
   }

};


#endif