//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionResult.mqh                                    |
//| Layer   : Core / Execution / Models                              |
//| Version : 3.0.0                                                  |
//| Purpose : Execution Result                                       |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_MODELS_EXECUTIONRESULT_MQH
#define CORE_EXECUTION_MODELS_EXECUTIONRESULT_MQH

//--------------------------------------------------
// Execution Status
//--------------------------------------------------

enum ENUM_EXECUTION_STATUS
{
   EXECUTION_UNKNOWN = 0,
   EXECUTION_SUCCESS,
   EXECUTION_REJECTED,
   EXECUTION_FAILED
};

//--------------------------------------------------
// Execution Result
//--------------------------------------------------

class CExecutionResult
{
public:

   bool Success;

   ENUM_EXECUTION_STATUS Status;

   ENUM_ORDER_TYPE OrderType;

   double LotSize;

   double EntryPrice;

   double StopLoss;

   double TakeProfit;

   ulong MagicNumber;

   ulong Ticket;

   string Comment;

   string Message;

public:

   //--------------------------------------------------

   CExecutionResult()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Success = false;

      Status = EXECUTION_UNKNOWN;

      OrderType = ORDER_TYPE_BUY;

      LotSize = 0.0;

      EntryPrice = 0.0;

      StopLoss = 0.0;

      TakeProfit = 0.0;

      MagicNumber = 0;

      Ticket = 0;

      Comment = "";

      Message = "";
   }
};

#endif