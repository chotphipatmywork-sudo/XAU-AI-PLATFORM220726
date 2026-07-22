//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioExposure.mqh                                  |
//| Layer   : Core / Portfolio                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Exposure Calculator                          |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_PORTFOLIOEXPOSURE_MQH
#define CORE_PORTFOLIO_PORTFOLIOEXPOSURE_MQH

#include "models/PortfolioSnapshot.mqh"

//--------------------------------------------------

class CPortfolioExposure
{
public:

   //--------------------------------------------------

   bool Calculate(
      CPortfolioSnapshot &snapshot)
   {
      snapshot.Reset();

      snapshot.Balance =
         AccountInfoDouble(ACCOUNT_BALANCE);

      snapshot.Equity =
         AccountInfoDouble(ACCOUNT_EQUITY);

      snapshot.Margin =
         AccountInfoDouble(ACCOUNT_MARGIN);

      snapshot.FreeMargin =
         AccountInfoDouble(ACCOUNT_MARGIN_FREE);

      snapshot.TotalPositions =
         PositionsTotal();

      snapshot.TotalFloatingProfit = 0.0;

      for(int i = 0; i < PositionsTotal(); i++)
      {
         ulong ticket = PositionGetTicket(i);

         if(ticket == 0)
            continue;

         snapshot.TotalFloatingProfit +=
            PositionGetDouble(POSITION_PROFIT);
      }

      snapshot.TotalExposurePercent = 0.0;

      if(snapshot.Equity > 0.0)
      {
         snapshot.TotalExposurePercent =
            (snapshot.Margin / snapshot.Equity) * 100.0;
      }

      snapshot.Valid = true;

      return true;
   }

};

#endif