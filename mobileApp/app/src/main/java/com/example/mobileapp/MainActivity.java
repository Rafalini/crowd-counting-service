package com.example.mobileapp;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class MainActivity extends AppCompatActivity {

    EditText editText;
    ImageView imageView;
    Button btopen;
    String message="message__";
    String logTag = "mojeLogTAK";

    private static String hostIp = "10.0.2.2";

    private static Socket clientSocket;
    private static InputStreamReader input;
    private static PrintWriter writer;
    private static final int REQEST_IMAGE = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        editText = (EditText) findViewById(R.id.messageTextField);
        imageView = (ImageView) findViewById(R.id.imageView);
        message = editText.getText().toString();
        Log.d(logTag,"Main scene created");

        if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.CAMERA},REQEST_IMAGE);
        }
    }

    public void takePicture(View view){
        Intent imageTakeIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(imageTakeIntent,REQEST_IMAGE);
    }

    @Override
    protected void onActivityResult(int requestCode, int result, Intent data) {

        if(requestCode==REQEST_IMAGE && result == RESULT_OK){
            Bundle extras = data.getExtras();
            Bitmap image = (Bitmap) extras.get("data");
            imageView.setImageBitmap(image);
        }

        super.onActivityResult(requestCode, result, data);
    }

    public void send_message(View view){
        Log.d(logTag,"send message task");
        MyTask mt = new MyTask();
        mt.execute();
        Toast.makeText(getApplicationContext(), "Data sent", Toast.LENGTH_LONG).show();
    }

    class MyTask extends AsyncTask<Void,Void,Void>{

        @Override
        protected Void doInBackground(Void... voids) {
            Log.d(logTag,"execution");
            try {
                Log.d(logTag,"try "+hostIp);
                clientSocket = new Socket("10.0.2.2", 7777);
                Log.d(logTag,"sock open");
                writer = new PrintWriter(clientSocket.getOutputStream());
                Log.d(logTag,"sending: "+message);
                writer.println("wiadomosc 123123");
                writer.flush();
                writer.close();
                clientSocket.close();
                Log.d(logTag,"socket close");

            } catch (Exception e) {
                Log.d(logTag, "exception ocurred");
                e.printStackTrace();
            }
            return null;
        }
    }
}