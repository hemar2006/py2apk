package ${package_name};

import android.app.AppCompatActivity;
import android.os.Bundle;
import android.content.Intent;
import android.os.Handler;

public class SplashActivity extends AppCompatActivity {

  private final int SPLASH_DISPLAY_DURATION = 3000;

  @Override
  public void onCreate(Bundle bundle) {
      super.onCreate(bundle);
      new Handler().postDelayed(new Runnable(){
          @Override
          public void run() {
              Intent mainIntent = new Intent(SplashActivity.this, MainActivity.class);
              SplashActivity.this.startActivity(mainIntent);
              SplashActivity.this.finish();
          }
      }, SPLASH_DISPLAY_DURATION);
  }
}
