package ${package_name};

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.os.Handler;

public class SplashActivity extends Activity {    

    @Override    
    public void onCreate(Bundle savedInstanceState) {       
        super.onCreate(savedInstanceState);        
	new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {                
                Intent mainIntent = new Intent(SplashActivity.this, MainActivity.class);
                startActivity(mainIntent);
                finish();
            }
        }, 2000);         
    }
}
