//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ApplicationState.mqh                                   |
//| Layer   : Core / Application                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Application lifecycle state management                 |
//+------------------------------------------------------------------+

#ifndef CORE_APPLICATION_APPLICATIONSTATE_MQH
#define CORE_APPLICATION_APPLICATIONSTATE_MQH


//+------------------------------------------------------------------+
//| Application State Enum                                           |
//+------------------------------------------------------------------+

enum ENUM_APPLICATION_STATE
{
   APPLICATION_STATE_CREATED = 0,
   APPLICATION_STATE_INITIALIZING,
   APPLICATION_STATE_READY,
   APPLICATION_STATE_RUNNING,
   APPLICATION_STATE_STOPPING,
   APPLICATION_STATE_STOPPED,
   APPLICATION_STATE_ERROR
};


//+------------------------------------------------------------------+
//| Application State Controller                                     |
//+------------------------------------------------------------------+

class CApplicationState
{

private:

   ENUM_APPLICATION_STATE m_state;


public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CApplicationState()
   {
      m_state = APPLICATION_STATE_CREATED;
   }



   //--------------------------------------------------
   // Set State
   //--------------------------------------------------

   void SetState(
      ENUM_APPLICATION_STATE state)
   {
      m_state = state;
   }



   //--------------------------------------------------
   // Get State
   //--------------------------------------------------

   ENUM_APPLICATION_STATE GetState() const
   {
      return m_state;
   }



   //--------------------------------------------------
   // Lifecycle Checks
   //--------------------------------------------------

   bool IsReady() const
   {
      return (
         m_state == APPLICATION_STATE_READY ||
         m_state == APPLICATION_STATE_RUNNING
      );
   }



   bool IsRunning() const
   {
      return (
         m_state == APPLICATION_STATE_RUNNING
      );
   }



   bool IsStopped() const
   {
      return (
         m_state == APPLICATION_STATE_STOPPED
      );
   }



   bool HasError() const
   {
      return (
         m_state == APPLICATION_STATE_ERROR
      );
   }



   //--------------------------------------------------
   // Lifecycle Transitions
   //--------------------------------------------------

   void Initialize()
   {
      m_state = APPLICATION_STATE_INITIALIZING;
   }



   void Start()
   {
      m_state = APPLICATION_STATE_RUNNING;
   }



   void Ready()
   {
      m_state = APPLICATION_STATE_READY;
   }



   void Stop()
   {
      m_state = APPLICATION_STATE_STOPPING;
   }



   void CompleteStop()
   {
      m_state = APPLICATION_STATE_STOPPED;
   }



   void Error()
   {
      m_state = APPLICATION_STATE_ERROR;
   }


};


#endif
//+------------------------------------------------------------------+