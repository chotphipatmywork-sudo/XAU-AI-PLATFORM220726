//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionAssembler.mqh                                 |
//| Layer   : Core / Execution / Assembler                           |
//| Version : 2.1.0                                                  |
//| Purpose : Build Final Execution Result                           |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_ASSEMBLER_EXECUTIONASSEMBLER_MQH
#define CORE_EXECUTION_ASSEMBLER_EXECUTIONASSEMBLER_MQH


#include "../models/ExecutionResult.mqh"


//--------------------------------------------------
// Execution Assembler
//--------------------------------------------------

class CExecutionAssembler
{


private:


   void CopyResult(
      const CExecutionResult &source,
      CExecutionResult &target)
   {

      target.Reset();


      target.Success =
         source.Success;


      target.Status =
         source.Status;


      target.OrderType =
         source.OrderType;


      target.LotSize =
         source.LotSize;


      target.EntryPrice =
         source.EntryPrice;


      target.StopLoss =
         source.StopLoss;


      target.TakeProfit =
         source.TakeProfit;


      target.MagicNumber =
         source.MagicNumber;


      target.Ticket =
         source.Ticket;


      target.Comment =
         source.Comment;


      target.Message =
         source.Message;

   }



public:


   //--------------------------------------------------
   // Build Final Result
   //--------------------------------------------------

   CExecutionResult Assemble(
      const CExecutionResult &source)
   {

      CExecutionResult result;


      CopyResult(
         source,
         result);


      return result;

   }



   //--------------------------------------------------
   // Success Helper
   //--------------------------------------------------

   bool IsSuccess(
      const CExecutionResult &result) const
   {
      return result.Success;
   }


};


#endif

//+------------------------------------------------------------------+