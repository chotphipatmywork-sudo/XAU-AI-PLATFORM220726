//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskResult.mqh                                         |
//| Layer   : Core / Risk / Models                                   |
//| Version : 3.1.0                                                  |
//| Purpose : Risk Analysis Result                                   |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_MODELS_RISKRESULT_MQH
#define CORE_RISK_MODELS_RISKRESULT_MQH


//--------------------------------------------------
// Risk Level
//--------------------------------------------------

enum ENUM_RISK_LEVEL
{
   RISK_UNKNOWN = 0,
   RISK_SAFE,
   RISK_WARNING,
   RISK_BLOCK
};


//--------------------------------------------------
// Risk Result
//--------------------------------------------------

class CRiskResult
{

public:

   // Permission
   bool AllowTrade;


   // Recommended Risk Percentage
   double RecommendedRisk;


   // Risk Classification
   ENUM_RISK_LEVEL Level;


   // Risk Score
   double Score;


   // Emergency Protection
   bool EmergencyStop;


   // Validation
   bool Valid;


   // Message
   string Message;



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CRiskResult()
   {
      Reset();
   }



   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {

      AllowTrade = false;

      RecommendedRisk = 0.0;

      Level = RISK_UNKNOWN;

      Score = 0.0;

      EmergencyStop = false;

      Valid = false;

      Message = "";

   }



   //--------------------------------------------------
   // Accept
   //--------------------------------------------------

   void Accept(string msg)
   {

      AllowTrade = true;

      RecommendedRisk = 0.0;

      Level = RISK_SAFE;

      EmergencyStop = false;

      Valid = true;

      Message = msg;

   }



   //--------------------------------------------------
   // Reject
   //--------------------------------------------------

   void Reject(string msg)
   {

      AllowTrade = false;

      Valid = true;

      Level = RISK_BLOCK;

      // Normal trade rejection
      // EmergencyStop reserved for protection modules
      EmergencyStop = false;

      Message = msg;

   }


};


#endif

//+------------------------------------------------------------------+
