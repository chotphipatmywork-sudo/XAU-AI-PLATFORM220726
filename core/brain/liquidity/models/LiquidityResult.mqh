//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityResult.mqh                                    |
//| Layer   : Brain / Liquidity / Models                             |
//| Version : 1.1.0                                                  |
//| Purpose : Final Liquidity Analysis Result                        |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_MODELS_LIQUIDITYRESULT_MQH
#define CORE_BRAIN_LIQUIDITY_MODELS_LIQUIDITYRESULT_MQH

//--------------------------------------------------
// Liquidity State
//--------------------------------------------------

enum ENUM_LIQUIDITY_STATE
{
   LIQUIDITY_UNKNOWN = 0,

   LIQUIDITY_LOW,

   LIQUIDITY_NORMAL,

   LIQUIDITY_HIGH,

   LIQUIDITY_SWEEP,

   LIQUIDITY_GRAB
};

//--------------------------------------------------
// Liquidity Result
//--------------------------------------------------

class CLiquidityResult
{
public:

   ENUM_LIQUIDITY_STATE State;

   double Score;

   bool BuySideLiquidity;

   bool SellSideLiquidity;

   bool SweepDetected;

   bool BuySideSweep;

   bool SellSideSweep;

   double RangePosition;

   double SweepDirection;

   double Confidence;

   //--------------------------------------------------

   CLiquidityResult()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      State = LIQUIDITY_UNKNOWN;

      Score = 0.0;

      BuySideLiquidity = false;

      SellSideLiquidity = false;

      SweepDetected = false;

      BuySideSweep = false;

      SellSideSweep = false;

      RangePosition = 50.0;

      SweepDirection = 50.0;

      Confidence = 0.0;
   }
};

#endif
