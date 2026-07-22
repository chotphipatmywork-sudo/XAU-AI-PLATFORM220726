//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModuleRegistry.mqh                                     |
//| Layer   : Core / Application                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Module Registration & State Management                |
//+------------------------------------------------------------------+

#ifndef CORE_APPLICATION_MODULEREGISTRY_MQH
#define CORE_APPLICATION_MODULEREGISTRY_MQH


//--------------------------------------------------
// Module State
//--------------------------------------------------

enum ENUM_MODULE_STATE
{
   MODULE_UNKNOWN = 0,
   MODULE_REGISTERED,
   MODULE_READY,
   MODULE_RUNNING,
   MODULE_ERROR
};


//--------------------------------------------------
// Module Registry
//--------------------------------------------------

class CModuleRegistry
{

private:

   ENUM_MODULE_STATE m_brain;

   ENUM_MODULE_STATE m_ai;

   ENUM_MODULE_STATE m_risk;

   ENUM_MODULE_STATE m_money;

   ENUM_MODULE_STATE m_execution;

   ENUM_MODULE_STATE m_dashboard;


public:


   //--------------------------------------------------

   CModuleRegistry()
   {
      Reset();
   }


   //--------------------------------------------------

   void Reset()
   {
      m_brain      = MODULE_UNKNOWN;

      m_ai         = MODULE_UNKNOWN;

      m_risk       = MODULE_UNKNOWN;

      m_money      = MODULE_UNKNOWN;

      m_execution  = MODULE_UNKNOWN;

      m_dashboard  = MODULE_UNKNOWN;
   }


   //--------------------------------------------------
   // Register Modules
   //--------------------------------------------------

   void RegisterAll()
   {
      m_brain      = MODULE_REGISTERED;

      m_ai         = MODULE_REGISTERED;

      m_risk       = MODULE_REGISTERED;

      m_money      = MODULE_REGISTERED;

      m_execution  = MODULE_REGISTERED;

      m_dashboard  = MODULE_REGISTERED;
   }


   //--------------------------------------------------

   void SetReady()
   {
      m_brain      = MODULE_READY;

      m_ai         = MODULE_READY;

      m_risk       = MODULE_READY;

      m_money      = MODULE_READY;

      m_execution  = MODULE_READY;

      m_dashboard  = MODULE_READY;
   }


   //--------------------------------------------------

   bool IsReady()
   {
      return (
         m_brain      == MODULE_READY &&
         m_ai         == MODULE_READY &&
         m_risk       == MODULE_READY &&
         m_money      == MODULE_READY &&
         m_execution  == MODULE_READY
      );
   }


   //--------------------------------------------------

   void Start()
   {
      if(IsReady())
      {
         m_brain      = MODULE_RUNNING;
         m_ai         = MODULE_RUNNING;
         m_risk       = MODULE_RUNNING;
         m_money      = MODULE_RUNNING;
         m_execution  = MODULE_RUNNING;
         m_dashboard  = MODULE_RUNNING;
      }
   }


   //--------------------------------------------------

   bool IsRunning()
   {
      return (
         m_brain == MODULE_RUNNING &&
         m_ai == MODULE_RUNNING &&
         m_risk == MODULE_RUNNING &&
         m_money == MODULE_RUNNING &&
         m_execution == MODULE_RUNNING
      );
   }


   //--------------------------------------------------

   ENUM_MODULE_STATE BrainState()
   {
      return m_brain;
   }


   ENUM_MODULE_STATE AIState()
   {
      return m_ai;
   }


   ENUM_MODULE_STATE RiskState()
   {
      return m_risk;
   }


   ENUM_MODULE_STATE MoneyState()
   {
      return m_money;
   }


   ENUM_MODULE_STATE ExecutionState()
   {
      return m_execution;
   }


   ENUM_MODULE_STATE DashboardState()
   {
      return m_dashboard;
   }

};


#endif
//+------------------------------------------------------------------+