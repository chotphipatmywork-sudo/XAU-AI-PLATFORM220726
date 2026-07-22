//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionAnalyzer.mqh                                   |
//| Layer   : Core / Position                                        |
//| Version : 1.1.0                                                  |
//| Purpose : Analyze Current Position                               |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONANALYZER_MQH
#define CORE_POSITION_POSITIONANALYZER_MQH

#include "models/PositionContext.mqh"
#include "models/PositionResult.mqh"

//--------------------------------------------------
// Position Analyzer
//--------------------------------------------------

class CPositionAnalyzer
{
public:

   //--------------------------------------------------

   CPositionResult Analyze(
      const CPositionContext &context)
   {
      CPositionResult result;

      result.Reset();


      //--------------------------------------------------
      // Symbol
      //--------------------------------------------------

      result.Symbol = context.Symbol;


      //--------------------------------------------------
      // Check Position
      //--------------------------------------------------

      if(PositionSelect(context.Symbol))
      {
         result.Valid = true;

         result.Status = POSITION_FOUND;


         result.Ticket =
            (ulong)PositionGetInteger(
               POSITION_TICKET);


         result.Type =
            (ENUM_POSITION_TYPE)
            PositionGetInteger(
               POSITION_TYPE);


         result.Volume =
            PositionGetDouble(
               POSITION_VOLUME);


         result.OpenPrice =
            PositionGetDouble(
               POSITION_PRICE_OPEN);


         result.CurrentPrice =
            PositionGetDouble(
               POSITION_PRICE_CURRENT);


         result.Profit =
            PositionGetDouble(
               POSITION_PROFIT);
      }
      else
      {
         result.Valid = true;

         result.Status =
            POSITION_NOT_FOUND;
      }


      return result;
   }

};

#endif